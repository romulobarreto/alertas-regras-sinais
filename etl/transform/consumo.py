"""Módulo para tratamento de dados de consumo mensal."""
import pandas as pd


def treat_monthly_consumption(df: pd.DataFrame) -> pd.DataFrame:
    """Substituir valores vazios por 0 nas colunas de meses de consumo."""
    df_copy = df.copy()

    # Identificar colunas que seguem o padrão MM/YYYY ou 'MM/YYYY'
    consumption_cols = [
        col
        for col in df_copy.columns
        if ('/' in str(col) and len(str(col).strip("'")) == 7)
    ]

    # Preencher vazios com 0 e garantir tipo numérico
    for col in consumption_cols:
        df_copy[col] = (
            pd.to_numeric(df_copy[col], errors='coerce').fillna(0).astype(int)
        )

    return df_copy
