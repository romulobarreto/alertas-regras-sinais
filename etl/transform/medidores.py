"""Módulo para enriquecimento de dados de medidores."""
import pandas as pd


def enrich_with_medidores(
    base_df: pd.DataFrame, medidores_df: pd.DataFrame
) -> pd.DataFrame:
    """Enriquecer a base com ANO e FABRICANTE a partir do MEDIDOR."""
    medidores = medidores_df.copy()

    # Converter MEDIDOR pra string (resolve problema 3 também)
    medidores['MEDIDOR'] = (
        medidores['medidor'].astype(str).str.strip().str.upper()
    )

    # Garantir que ANO é inteiro
    medidores['ANO'] = pd.to_numeric(medidores['ANO'], errors='coerce').astype(
        'Int64'
    )

    # Garantir 1 linha por medidor
    medidores = medidores.drop_duplicates(subset=['MEDIDOR'], keep='first')

    # Converter MEDIDOR da base também pra string
    base_df_copy = base_df.copy()
    base_df_copy['MEDIDOR'] = (
        base_df_copy['MEDIDOR'].astype(str).str.strip().str.upper()
    )

    df = base_df_copy.merge(
        medidores[['MEDIDOR', 'ANO', 'FABRICANTE']],
        on='MEDIDOR',
        how='left',
        validate='m:1',
    )
    return df
