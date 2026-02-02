"""Módulo para aplicação de regras de negócio complexas (automáticas)."""

from __future__ import annotations

import re
from datetime import datetime, timedelta
from typing import List, Tuple

import numpy as np
import pandas as pd

_MONTH_RE = re.compile(r"^'?(\d{2})/(\d{4})'?$")


def _get_consumption_month_cols(df: pd.DataFrame) -> List[str]:
    """Retorna colunas de consumo no formato MM/YYYY."""
    cols = []
    for c in df.columns:
        if _MONTH_RE.match(str(c).strip()):
            cols.append(c)
    return cols


def _month_key(col: str) -> Tuple[int, int]:
    """Chave de ordenação (ano, mes) a partir de 'MM/YYYY'."""
    m = _MONTH_RE.match(str(col).strip())
    if not m:
        return (0, 0)
    mm = int(m.group(1))
    yyyy = int(m.group(2))
    return (yyyy, mm)


def _normalize_month_col_name(col: str) -> str:
    """Remove aspas simples do nome, se tiver."""
    m = _MONTH_RE.match(str(col).strip())
    if not m:
        return str(col)
    return f'{m.group(1)}/{m.group(2)}'


def _get_reference_date(df: pd.DataFrame) -> datetime:
    """Retorna a data de referência (último mês disponível)."""
    month_cols = _get_consumption_month_cols(df)
    if not month_cols:
        return datetime.now()

    latest = max(month_cols, key=_month_key)
    year, month = _month_key(latest)
    return datetime(year, month, 1)


def _fiscalizacao_recente(
    fisc_date: pd.Series, ref_date: datetime, months: int
) -> pd.Series:
    """Verifica se houve fiscalização nos últimos N meses."""
    cutoff = ref_date - timedelta(days=months * 30)
    return fisc_date.notna() & (fisc_date >= cutoff)


def _has_fraude_historica(codigo: pd.Series) -> pd.Series:
    """Verifica se o código começa com '1' (fraude)."""
    return codigo.notna() & (codigo.astype(str).str.strip().str[0] == '1')


def calculate_yoy(df: pd.DataFrame) -> pd.DataFrame:
    """Calcula YoY em decimal e a média dos YoYs."""
    out = df.copy()
    month_cols_raw = _get_consumption_month_cols(out)

    if not month_cols_raw:
        out['MEDIA_YOY'] = pd.NA
        return out

    rename_map = {c: _normalize_month_col_name(c) for c in month_cols_raw}
    out = out.rename(columns=rename_map)
    month_cols = sorted(
        {rename_map[c] for c in month_cols_raw}, key=_month_key
    )

    latest = max(month_cols, key=_month_key)
    usable = [c for c in month_cols if c != latest]

    for c in month_cols:
        out[c] = pd.to_numeric(out[c], errors='coerce')

    yoy_cols = []
    for c in usable:
        year, month = _month_key(c)
        prev = f'{month:02d}/{year-1}'

        if prev in out.columns:
            yoy_name = f"yoy_{c.replace('/', '_')}"
            yoy_cols.append(yoy_name)
            out[yoy_name] = np.where(
                out[prev] > 0, (out[c] - out[prev]) / out[prev], np.nan
            )

    if yoy_cols:
        # Calcula a média e garante que seja um float decimal (ex: -0.40 para -40%)
        out['MEDIA_YOY'] = out[yoy_cols].mean(axis=1, skipna=True)

        # Se por algum motivo o número vier "inteiro" (ex: -40 em vez de -0.4)
        # fazemos uma trava de segurança:
        mask_grande = (
            out['MEDIA_YOY'].abs() > 2
        )   # Ninguém cai 200% ou sobe 200% normalmente aqui
        out.loc[mask_grande, 'MEDIA_YOY'] = (
            out.loc[mask_grande, 'MEDIA_YOY'] / 100
        )

        out['MEDIA_YOY'] = out['MEDIA_YOY'].round(4)
    else:
        out['MEDIA_YOY'] = pd.NA

    return out


def flag_minimum_by_phase(df: pd.DataFrame) -> pd.DataFrame:
    """Marca UCs que estão no mínimo nos últimos 4 meses (todos os meses)."""
    out = df.copy()
    month_cols_raw = _get_consumption_month_cols(out)

    if not month_cols_raw:
        out['NO_MINIMO_4M'] = pd.NA
        return out

    rename_map = {c: _normalize_month_col_name(c) for c in month_cols_raw}
    out = out.rename(columns=rename_map)
    month_cols = sorted(
        {rename_map[c] for c in month_cols_raw}, key=_month_key
    )

    latest = max(month_cols, key=_month_key)
    usable = [c for c in month_cols if c != latest]
    last_4 = usable[-4:] if len(usable) >= 4 else usable

    for c in month_cols:
        out[c] = pd.to_numeric(out[c], errors='coerce')

    status = out['STATUS_COMERCIAL'].astype(str).str.strip().str.upper()
    fase = out['FASE'].astype(str).str.strip().str.upper()

    out['NO_MINIMO_4M'] = pd.NA

    limits = {'MO': 40, 'BI': 60, 'TR': 110}

    for f, limit in limits.items():
        cond_fase = (status == 'LG') & (fase == f)
        count_below = (out[last_4] <= limit).sum(axis=1)
        out.loc[
            cond_fase & (count_below == len(last_4)), 'NO_MINIMO_4M'
        ] = 'SIM'

    return out


def apply_priority_rules(df: pd.DataFrame) -> pd.DataFrame:
    """Aplica todas as regras de priorização (P1, P2, P3) com hierarquia e filtro de esforço."""
    out = df.copy()
    ref_date = _get_reference_date(out)

    # Inicializa colunas
    out['PRIORIDADE'] = pd.NA
    out['MOTIVO_PRIORIDADE'] = pd.NA

    # --- PREPARAÇÃO DE DADOS ---
    status = out['STATUS_COMERCIAL'].astype(str).str.strip().str.upper()

    # Datas de Esforço (Fiscalização e Bate Caixa)
    fisc_date = pd.to_datetime(
        out.get('FISCALIZACAO', pd.Series(index=out.index)), errors='coerce'
    )
    bate_caixa = pd.to_datetime(
        out.get('BATE_CAIXA', pd.Series(index=out.index)), errors='coerce'
    )

    # Função interna para checar esforço em N meses
    def tem_esforco_recente(meses):
        f_rec = _fiscalizacao_recente(fisc_date, ref_date, meses)
        b_rec = _fiscalizacao_recente(bate_caixa, ref_date, meses)
        return f_rec | b_rec

    # Outros campos
    move_out = pd.to_datetime(
        out.get('MOVE_OUT', pd.Series(index=out.index)), errors='coerce'
    )
    has_nrt = out.get(
        'HAS_NRT', pd.Series(False, index=out.index)
    )   # Assumindo que já tratamos NRT
    has_fraude = _has_fraude_historica(
        out.get('COD', pd.Series(index=out.index))
    )
    no_minimo = out.get('NO_MINIMO_4M', pd.Series(index=out.index)) == 'SIM'
    media_yoy = pd.to_numeric(
        out.get('MEDIA_YOY', pd.Series(index=out.index)), errors='coerce'
    )
    fabricante = out['FABRICANTE'].fillna('').astype(str).str.upper()
    ano_medidor = pd.to_numeric(out['ANO'], errors='coerce').fillna(0)

    # Apontamentos
    apontamentos_relevantes = [
        'VESTIGIO DE IRREGULARIDADE',
        'VESTIGIO DE LIGACAO IRREGULAR',
        'PROB DISPLAY MEDIDOR ELETRONICO',
        'MEDIDOR COM VIDRO QUEBRADO',
        'MEDIDOR PARADO DESCONTROLADO OU EMBACADO',
        'MEDIDOR GIRANDO AO CONTRARIO',
        'MEDIDOR NAO LOCALIZADO',
        'MEDIDOR RETIRADO DA CAIXA DE MEDICAO',
        'NUMERO DO MEDIDOR NAO CONFERE',
        'MEDIDOR COM VIDRO EMBACADO (NAO PERMITE LEITURA)',
        'MEDIDOR DESENERGIZADO (NAO EXIBE LEITURA)',
        'IMPEDIMENTO DE LEITURA POR SINISTRO',
        'EQUIPAMENTO COM PERDA DE PARAMETRO',
        'ERRO DE CADASTRO',
        'TROCA DE EQUIPAMENTO POR ENCHENTE',
    ]
    has_apontamento = (
        out['LEITURISTA']
        .fillna('')
        .astype(str)
        .str.upper()
        .isin(apontamentos_relevantes)
    )

    # --- APLICAÇÃO DAS REGRAS (HIERARQUIA) ---

    # ========== P1 (ALERTAS) ==========
    # P1.1: DS + NRT - (Fisc/Bate Caixa após Move-out)
    esforco_apos_ds = (fisc_date > move_out) | (bate_caixa > move_out)
    cond_p1_1 = (status == 'DS') & has_nrt & ~esforco_apos_ds
    out.loc[cond_p1_1, ['PRIORIDADE', 'MOTIVO_PRIORIDADE']] = [
        'P1',
        'DESLIGADO COM RECLAMAÇÃO',
    ]

    # P1.2: LG + MINIMO + NRT - (Fisc/Bate Caixa 4 meses)
    cond_p1_2 = (
        (status == 'LG')
        & no_minimo
        & has_nrt
        & ~tem_esforco_recente(4)
        & out['PRIORIDADE'].isna()
    )
    out.loc[cond_p1_2, ['PRIORIDADE', 'MOTIVO_PRIORIDADE']] = [
        'P1',
        'MÍNIMO DA FASE COM RECLAMAÇÃO',
    ]

    # ========== P2 (REGRAS) ==========
    # P2.1: LG + REINCIDENTE + QUEDA 40% - (Fisc/Bate Caixa 6 meses)
    cond_p2_1 = (
        (status == 'LG')
        & has_fraude
        & (media_yoy <= -0.4)
        & ~tem_esforco_recente(6)
        & out['PRIORIDADE'].isna()
    )
    out.loc[cond_p2_1, ['PRIORIDADE', 'MOTIVO_PRIORIDADE']] = [
        'P2',
        'REINCIDENTE COM QUEDA DE CONSUMO',
    ]

    # P2.2: LG + MINIMO + APONTAMENTO - (Fisc/Bate Caixa 4 meses)
    cond_p2_2 = (
        (status == 'LG')
        & no_minimo
        & has_apontamento
        & ~tem_esforco_recente(4)
        & out['PRIORIDADE'].isna()
    )
    out.loc[cond_p2_2, ['PRIORIDADE', 'MOTIVO_PRIORIDADE']] = [
        'P2',
        'MÍNIMO COM APONTAMENTO SUSPEITO',
    ]

    # P2.3: DOWERTECH + 2014 + LG + MINIMO - (Fisc/Bate Caixa 4 meses)
    cond_p2_3 = (
        fabricante.str.contains('DOWERTECH', na=False)
        & (ano_medidor == 2014)
        & (status == 'LG')
        & no_minimo
        & ~tem_esforco_recente(4)
        & out['PRIORIDADE'].isna()
    )
    out.loc[cond_p2_3, ['PRIORIDADE', 'MOTIVO_PRIORIDADE']] = [
        'P2',
        'MEDIDOR DOWERTECH 2014 NO MÍNIMO',
    ]

    # P2.4: ANO <= 2000 + LG + MINIMO - (Fisc/Bate Caixa 4 meses)
    cond_p2_4 = (
        (ano_medidor <= 2000)
        & (status == 'LG')
        & no_minimo
        & ~tem_esforco_recente(4)
        & out['PRIORIDADE'].isna()
    )
    out.loc[cond_p2_4, ['PRIORIDADE', 'MOTIVO_PRIORIDADE']] = [
        'P2',
        'MEDIDOR ANTIGO NO MÍNIMO',
    ]

    # ========== P3 (SINAIS) ==========
    # P3.1: CONDOMINIOS ALTO DS (Lógica de agrupamento)
    cond_col = out['CONDOMINIO'].fillna('').astype(str).str.upper()
    if 'ENDERECO' in out.columns:
        # Agrupa por endereço (simplificado) para achar condomínios com >= 5 DS
        ds_por_endereco = out[status == 'DS'].groupby('ENDERECO').size()
        enderecos_criticos = ds_por_endereco[ds_por_endereco >= 5].index
        cond_p3_1 = (
            (cond_col == 'SIM')
            & out['ENDERECO'].isin(enderecos_criticos)
            & out['PRIORIDADE'].isna()
        )
        out.loc[cond_p3_1, ['PRIORIDADE', 'MOTIVO_PRIORIDADE']] = [
            'P3',
            'CONDOMÍNIO COM ALTO ÍNDICE DE DS',
        ]

    # P3.2: DS RECENTE (6m) + FRAUDE - (Fisc/Bate Caixa após Move-out)
    ds_recente = move_out >= (ref_date - timedelta(days=180))
    cond_p3_2 = (
        (status == 'DS')
        & ds_recente
        & has_fraude
        & ~esforco_apos_ds
        & out['PRIORIDADE'].isna()
    )
    out.loc[cond_p3_2, ['PRIORIDADE', 'MOTIVO_PRIORIDADE']] = [
        'P3',
        'DESLIGADO RECENTE COM HISTÓRICO DE FRAUDE',
    ]

    # P3.3: LG + MINIMO - (Fisc/Bate Caixa 4 meses)
    cond_p3_3 = (
        (status == 'LG')
        & no_minimo
        & ~tem_esforco_recente(4)
        & out['PRIORIDADE'].isna()
    )
    out.loc[cond_p3_3, ['PRIORIDADE', 'MOTIVO_PRIORIDADE']] = [
        'P3',
        'CONSUMO NO MÍNIMO DA FASE',
    ]

    # P3.4: LG + QUEDA 40% - (Fisc/Bate Caixa 6 meses)
    cond_p3_4 = (
        (status == 'LG')
        & (media_yoy <= -0.4)
        & ~tem_esforco_recente(6)
        & out['PRIORIDADE'].isna()
    )
    out.loc[cond_p3_4, ['PRIORIDADE', 'MOTIVO_PRIORIDADE']] = [
        'P3',
        'QUEDA ACENTUADA DE CONSUMO',
    ]

    return out
