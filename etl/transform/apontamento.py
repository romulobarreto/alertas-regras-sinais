"""Módulo para enriquecimento de dados de apontamento de leitura."""
import pandas as pd


def treat_apontamento_codes(
    apontamento_df: pd.DataFrame, codigos_df: pd.DataFrame
) -> pd.DataFrame:
    """Primeira etapa: enriquecer apontamento com descrição dos códigos."""
    apontamento = apontamento_df.copy()
    codigos = codigos_df.copy()

    # Renomear coluna de código para match
    codigos = codigos.rename(columns={'Apontamento': 'COD_MENS_LEF'})

    # Garantir tipo numérico
    apontamento['COD_MENS_LEF'] = pd.to_numeric(
        apontamento['COD_MENS_LEF'], errors='coerce'
    ).astype('Int64')
    codigos['COD_MENS_LEF'] = pd.to_numeric(
        codigos['COD_MENS_LEF'], errors='coerce'
    ).astype('Int64')

    # Merge
    apontamento = apontamento.merge(
        codigos[['COD_MENS_LEF', 'Descricao']],
        on='COD_MENS_LEF',
        how='left',
    )

    return apontamento


def enrich_with_apontamento(
    base_df: pd.DataFrame, apontamento_treated_df: pd.DataFrame
) -> pd.DataFrame:
    """Segunda etapa: enriquecer base com descrição do apontamento."""
    apontamento = apontamento_treated_df.copy()

    # Renomear para padronizar
    apontamento = apontamento.rename(
        columns={'INSTALACAO': 'UC', 'Descricao': 'LEITURISTA'}
    )

    # --- LÓGICA PROCV: Pegar apenas a primeira ocorrência (já que está ordenado) ---
    apontamento = apontamento.drop_duplicates(subset=['UC'], keep='first')

    # Garantir tipo numérico
    apontamento['UC'] = pd.to_numeric(
        apontamento['UC'], errors='coerce'
    ).astype('Int64')
    base_df_copy = base_df.copy()
    base_df_copy['UC'] = pd.to_numeric(
        base_df_copy['UC'], errors='coerce'
    ).astype('Int64')

    # Merge com validação m:1 (muitos para um)
    df = base_df_copy.merge(
        apontamento[['UC', 'LEITURISTA']], on='UC', how='left', validate='m:1'
    )
    return df
