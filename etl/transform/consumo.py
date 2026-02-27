"""Módulo para tratamento de dados de consumo mensal."""
from __future__ import annotations

import re

import pandas as pd

_MONTH_COL_RE = re.compile(r'^\d{2}/\d{4}$')


def _is_month_col(col_name: object) -> bool:
    """Retorna True se col_name corresponde ao padrão MM/YYYY (aceita quotes e espaços)."""
    if col_name is None:
        return False
    s = str(col_name).strip().strip("'").strip()
    return bool(_MONTH_COL_RE.match(s))


def treat_monthly_consumption(df: pd.DataFrame) -> pd.DataFrame:
    """
    Substituir valores vazios por 0 nas colunas de meses de consumo (MM/YYYY).

    - Detecta colunas com padrão preciso MM/YYYY.
    - Converte os valores para numérico (coerce), preenche NaN por 0 e cast para int.
    - Calcula a média de consumo mensal e armazena em CONSUMO_MEDIO.
    - Não altera outras colunas.
    """
    df_copy = df.copy()

    consumption_cols = [col for col in df_copy.columns if _is_month_col(col)]

    for col in consumption_cols:
        df_copy[col] = (
            pd.to_numeric(df_copy[col], errors='coerce').fillna(0).astype(int)
        )

    if consumption_cols:
        df_copy['CONSUMO_MEDIO'] = (
            df_copy[consumption_cols]
            .replace(0, pd.NA)
            .mean(axis=1, skipna=True)
            .round(2)
        )
    else:
        df_copy['CONSUMO_MEDIO'] = pd.NA

    return df_copy