"""Módulo para enriquecimento de dados de inspeções."""
import pandas as pd


def enrich_with_inspections(
    base_df: pd.DataFrame, inspections_df: pd.DataFrame
) -> pd.DataFrame:
    """Enriquecer a base com data de fiscalização e código de inspeção."""
    inspections = inspections_df.copy()
    inspections['DATA_EXECUCAO'] = pd.to_datetime(inspections['DATA_EXECUCAO'])
    inspections = inspections.sort_values('DATA_EXECUCAO').drop_duplicates(
        'UC / MD', keep='last'
    )

    inspections = inspections.rename(
        columns={
            'UC / MD': 'UC',
            'DATA_EXECUCAO': 'FISCALIZACAO',
            'COD': 'COD',
        }
    )

    # Forçar COD como inteiro
    inspections['COD'] = pd.to_numeric(
        inspections['COD'], errors='coerce'
    ).astype('Int64')

    df = base_df.merge(
        inspections[['UC', 'FISCALIZACAO', 'COD']],
        on='UC',
        how='left',
        validate='m:1',
    )

    return df
