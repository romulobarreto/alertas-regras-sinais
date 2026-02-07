"""Módulo para enriquecimento com dados de prospecção de alvos."""

from __future__ import annotations

import re
from typing import Optional

import pandas as pd

_ISO_DATE_RE = re.compile(r'^\d{4}-\d{2}-\d{2}$')


def _safe_parse_dates(series: pd.Series) -> pd.Series:
    """Parse seguro que prioriza YYYY-MM-DD (ISO) com formato explícito e para os demais casos, usa dayfirst=True."""
    s = series.astype(str).fillna('')
    out = pd.Series(pd.NaT, index=series.index, dtype='datetime64[ns]')

    # máscara para ISO (YYYY-MM-DD)
    mask_iso = s.str.match(_ISO_DATE_RE)

    if mask_iso.any():
        out.loc[mask_iso] = pd.to_datetime(
            s.loc[mask_iso], format='%Y-%m-%d', errors='coerce'
        )

    # para o resto, tenta parse genérico com dayfirst=True
    if (~mask_iso).any():
        out.loc[~mask_iso] = pd.to_datetime(
            s.loc[~mask_iso], errors='coerce', dayfirst=True
        )

    return out


def enrich_with_prospeccao(
    df_cadastro: pd.DataFrame, df_prospeccao: pd.DataFrame
) -> pd.DataFrame:
    """Traz a última conclusão e data do prospector para a base principal.

    Retorna DATA_PROSPECTOR como datetime (NaT quando não existir) e
    CONCLUSAO_PROSPECTOR como string (limpa). A formatação final para
    'dd/mm/YYYY' deve ser feita no main.py no momento de saída, para
    manter consistência com as outras fontes.
    """
    if df_prospeccao is None or df_prospeccao.empty:
        df_cadastro['DATA_PROSPECTOR'] = pd.NaT
        df_cadastro['CONCLUSAO_PROSPECTOR'] = pd.NA
        return df_cadastro

    pros = df_prospeccao.copy()

    # Normaliza nomes esperados — tenta encontrar colunas com nomes comuns
    # (assume que a planilha tem colunas 'UC', 'DATA', 'CONCLUSAO').
    for col in ['UC', 'DATA', 'CONCLUSAO']:
        if col not in pros.columns:
            matches = [c for c in pros.columns if c.strip().upper() == col]
            if matches:
                pros = pros.rename(columns={matches[0]: col})

    # Garante datetime na coluna de data usando parser seguro
    pros['DATA'] = _safe_parse_dates(pros['DATA'])

    # Limpa UC (remove .0, espaços)
    pros['UC'] = (
        pros['UC'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
    )

    # Pega a última entrada por UC (mais recente)
    pros = pros.sort_values('DATA', ascending=False)
    pros = pros.drop_duplicates(subset=['UC'], keep='first')

    # Renomeia para colunas de saída
    pros = pros.rename(
        columns={
            'DATA': 'DATA_PROSPECTOR',
            'CONCLUSAO': 'CONCLUSAO_PROSPECTOR',
        }
    )

    # Prepara base principal para merge
    df = df_cadastro.copy()
    df['UC_STR'] = (
        df['UC'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
    )

    out = df.merge(
        pros[['UC', 'DATA_PROSPECTOR', 'CONCLUSAO_PROSPECTOR']],
        left_on='UC_STR',
        right_on='UC',
        how='left',
        suffixes=('', '_pros'),
    )

    # Limpeza de colunas auxiliares
    if 'UC_pros' in out.columns:
        out = out.drop(columns=['UC_pros'])
    out = out.drop(columns=['UC_STR'])

    # Normaliza a conclusão (string limpa)
    out['CONCLUSAO_PROSPECTOR'] = (
        out['CONCLUSAO_PROSPECTOR'].astype(str).fillna('').str.strip()
    )

    return out
