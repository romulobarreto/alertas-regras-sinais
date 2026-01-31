"""Módulo para aplicação de regras de negócio complexas (automáticas)."""

from __future__ import annotations

import re
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
            # Cálculo em decimal (sem multiplicar por 100)
            out[yoy_name] = np.where(
                out[prev] > 0, (out[c] - out[prev]) / out[prev], np.nan
            )

    if yoy_cols:
        out['MEDIA_YOY'] = out[yoy_cols].mean(axis=1, skipna=True).round(6)
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

    # Regra: TODOS os meses (count == len(last_4)) devem estar abaixo do limite
    limits = {'MO': 40, 'BI': 60, 'TR': 110}

    for f, limit in limits.items():
        cond_fase = (status == 'LG') & (fase == f)
        # Conta quantos meses estão abaixo do limite
        count_below = (out[last_4] <= limit).sum(axis=1)
        # Se o contador for igual ao número de meses analisados, todos estão no mínimo
        out.loc[
            cond_fase & (count_below == len(last_4)), 'NO_MINIMO_4M'
        ] = 'SIM'

    return out
