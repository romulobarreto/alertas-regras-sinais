"""Módulo para enriquecimento de dados de medidores."""
from __future__ import annotations

import pandas as pd


def enrich_with_medidores(
    base_df: pd.DataFrame, medidores_df: pd.DataFrame
) -> pd.DataFrame:
    """Enriquecer a base com ANO e FABRICANTE a partir do MEDIDOR.

    Mantém a lógica de comparação por string (case-insensitive e sem espaços).
    """
    medidores = medidores_df.copy()

    # Validação da coluna de origem
    if 'medidor' not in medidores.columns:
        raise KeyError(
            "A base de medidores precisa ter a coluna 'medidor' (minúsculo)."
        )

    # Converter MEDIDOR pra string e normalizar
    medidores['MEDIDOR_JOIN'] = (
        medidores['medidor'].astype(str).str.strip().str.upper()
    )

    # Garantir que ANO é numérico (Int64 permite NA)
    medidores['ANO'] = pd.to_numeric(medidores['ANO'], errors='coerce').astype(
        'Int64'
    )

    # Limpeza básica no fabricante
    if 'FABRICANTE' in medidores.columns:
        medidores['FABRICANTE'] = (
            medidores['FABRICANTE'].astype(str).str.strip().str.upper()
        )

    # Garantir 1 linha por medidor (PROCV)
    medidores = medidores.drop_duplicates(
        subset=['MEDIDOR_JOIN'], keep='first'
    )

    # Preparar a base principal para o merge
    base_df_copy = base_df.copy()
    base_df_copy['MEDIDOR_JOIN'] = (
        base_df_copy['MEDIDOR'].astype(str).str.strip().str.upper()
    )

    # Merge
    df = base_df_copy.merge(
        medidores[['MEDIDOR_JOIN', 'ANO', 'FABRICANTE']],
        on='MEDIDOR_JOIN',
        how='left',
        validate='m:1',
    )

    # Remove a coluna auxiliar de join
    return df.drop(columns=['MEDIDOR_JOIN'])
