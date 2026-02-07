"""Módulo para enriquecimento de dados de inspeções."""
from __future__ import annotations

from typing import Dict

import pandas as pd


def enrich_with_inspections(
    base_df: pd.DataFrame, inspections_df: pd.DataFrame
) -> pd.DataFrame:
    """Enriquecer a base com data de fiscalização e código de inspeção.

    Regras:
    - Mantém apenas a última inspeção por UC (mais recente por DATA_EXECUCAO).
    - Retorna a coluna FISCALIZACAO (datetime) e COD (Int64) no resultado.
    """
    inspections = inspections_df.copy()

    # Valida colunas esperadas
    if 'UC / MD' not in inspections.columns:
        raise KeyError("A tabela de inspeções precisa ter a coluna 'UC / MD'.")
    if 'DATA_EXECUCAO' not in inspections.columns:
        raise KeyError(
            "A tabela de inspeções precisa ter a coluna 'DATA_EXECUCAO'."
        )
    if 'COD' not in inspections.columns:
        raise KeyError("A tabela de inspeções precisa ter a coluna 'COD'.")

    # Renomeia logo para facilitar manipulação
    inspections = inspections.rename(
        columns={'UC / MD': 'UC', 'DATA_EXECUCAO': 'FISCALIZACAO'}
    )

    # Parse seguro da data (coerce para NaT em valores inválidos)
    inspections['FISCALIZACAO'] = pd.to_datetime(
        inspections['FISCALIZACAO'], errors='coerce'
    )

    # Ordena e mantém apenas a última ocorrência por UC
    inspections = inspections.sort_values('FISCALIZACAO').drop_duplicates(
        'UC', keep='last'
    )

    # Normaliza tipos: UC e COD numéricos (UC como Int64 para permitir NA)
    inspections['UC'] = pd.to_numeric(
        inspections['UC'], errors='coerce'
    ).astype('Int64')
    inspections['COD'] = pd.to_numeric(
        inspections['COD'], errors='coerce'
    ).astype('Int64')

    # Merge com validação m:1 (muitos da base -> 1 inspeção)
    df = base_df.merge(
        inspections[['UC', 'FISCALIZACAO', 'COD']],
        on='UC',
        how='left',
        validate='m:1',
    )

    return df
