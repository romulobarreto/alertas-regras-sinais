"""Módulo para enriquecimento de dados de ocorrências."""
import pandas as pd


def enrich_with_occurrences(
    base_df: pd.DataFrame, occurrences_df: pd.DataFrame
) -> pd.DataFrame:
    """Enriquecer a base com data de ocorrência."""
    occurrences = occurrences_df.copy()

    occurrences = occurrences.rename(
        columns={'CR_NUMERO': 'UC', 'OCO_DATA_NR': 'NOTA_DE_RECLAMACAO'}
    )

    # --- LÓGICA PROCV: Pegar apenas a primeira ocorrência ---
    occurrences = occurrences.drop_duplicates(subset=['UC'], keep='first')

    occurrences['UC'] = pd.to_numeric(
        occurrences['UC'], errors='coerce'
    ).astype('Int64')
    base_df_copy = base_df.copy()
    base_df_copy['UC'] = pd.to_numeric(
        base_df_copy['UC'], errors='coerce'
    ).astype('Int64')

    df = base_df_copy.merge(
        occurrences[['UC', 'NOTA_DE_RECLAMACAO']],
        on='UC',
        how='left',
        validate='m:1',
    )
    return df
