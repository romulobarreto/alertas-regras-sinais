"""Módulo para enriquecimento de dados de apontamento de leitura."""

from __future__ import annotations

import pandas as pd


def treat_apontamento_codes(
    apontamento_df: pd.DataFrame, codigos_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Enriquecer apontamento com descrição dos códigos.

    Parâmetros:
    - apontamento_df: DataFrame com dados de apontamento, deve ter coluna 'COD_MENS_LEF'.
    - codigos_df: DataFrame com códigos e descrições, deve ter coluna 'Apontamento'.

    Retorna:
    - DataFrame apontamento com coluna 'Descricao' adicionada via merge.
    """
    apontamento = apontamento_df.copy()
    codigos = codigos_df.copy()

    if 'COD_MENS_LEF' not in apontamento.columns:
        raise KeyError(
            "Coluna 'COD_MENS_LEF' não encontrada no apontamento_df"
        )
    if 'Apontamento' not in codigos.columns:
        raise KeyError("Coluna 'Apontamento' não encontrada no codigos_df")

    # Renomear coluna de código para match
    codigos = codigos.rename(columns={'Apontamento': 'COD_MENS_LEF'})

    # Garantir tipo numérico (Int64 para permitir NA)
    apontamento['COD_MENS_LEF'] = pd.to_numeric(
        apontamento['COD_MENS_LEF'], errors='coerce'
    ).astype('Int64')
    codigos['COD_MENS_LEF'] = pd.to_numeric(
        codigos['COD_MENS_LEF'], errors='coerce'
    ).astype('Int64')

    # Merge para trazer a descrição
    apontamento = apontamento.merge(
        codigos[['COD_MENS_LEF', 'Descricao']],
        on='COD_MENS_LEF',
        how='left',
    )

    return apontamento


def enrich_with_apontamento(
    base_df: pd.DataFrame, apontamento_treated_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Enriquecer base principal com descrição do apontamento (LEITURISTA).

    Parâmetros:
    - base_df: DataFrame principal com coluna 'UC'.
    - apontamento_treated_df: DataFrame tratado com colunas 'INSTALACAO' e 'Descricao'.

    Retorna:
    - DataFrame base_df enriquecido com coluna 'LEITURISTA'.
    """
    apontamento = apontamento_treated_df.copy()

    if 'INSTALACAO' not in apontamento.columns:
        raise KeyError(
            "Coluna 'INSTALACAO' não encontrada no apontamento_treated_df"
        )
    if 'Descricao' not in apontamento.columns:
        raise KeyError(
            "Coluna 'Descricao' não encontrada no apontamento_treated_df"
        )
    if 'UC' not in base_df.columns:
        raise KeyError("Coluna 'UC' não encontrada no base_df")

    # Renomear para padronizar
    apontamento = apontamento.rename(
        columns={'INSTALACAO': 'UC', 'Descricao': 'LEITURISTA'}
    )

    # Pega apenas a primeira ocorrência por UC (PROCV)
    apontamento = apontamento.drop_duplicates(subset=['UC'], keep='first')

    # Garantir tipo numérico para merge
    apontamento['UC'] = pd.to_numeric(
        apontamento['UC'], errors='coerce'
    ).astype('Int64')
    base_df_copy = base_df.copy()
    base_df_copy['UC'] = pd.to_numeric(
        base_df_copy['UC'], errors='coerce'
    ).astype('Int64')

    # Merge com validação m:1
    df = base_df_copy.merge(
        apontamento[['UC', 'LEITURISTA']], on='UC', how='left', validate='m:1'
    )
    return df
