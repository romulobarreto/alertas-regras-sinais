"""Módulo para enriquecimento de dados de ocorrências."""
import pandas as pd


def enrich_with_occurrences(
    base_df: pd.DataFrame, occurrences_df: pd.DataFrame
) -> pd.DataFrame:
    """Enriquecer a base com data de ocorrência e flag de NRT."""
    # 1. Limpeza da base de ocorrências
    occ = occurrences_df.copy()

    # Renomeia se os nomes originais forem diferentes
    occ = occ.rename(
        columns={'CR_NUMERO': 'UC', 'DT_OCO_INCLUSAO': 'NOTA DE RECLAMACAO'}
    )

    # Garante que UC seja string limpa (sem .0 e sem espaços)
    occ['UC'] = (
        occ['UC'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
    )

    # Remove duplicadas (PROCV: pega a primeira ocorrência)
    occ = occ.drop_duplicates(subset=['UC'], keep='first')

    # 2. Limpeza da base principal
    df = base_df.copy()
    df['UC'] = (
        df['UC'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
    )

    # 3. O MERGE (O PROCV propriamente dito)
    df = df.merge(occ[['UC', 'NOTA DE RECLAMACAO']], on='UC', how='left')

    # 4. Tratamento da Data e Flag
    # O pandas é inteligente: se vier 2026-01-30 ou 30/01/2026, o dayfirst=True ajuda
    df['NOTA DE RECLAMACAO'] = pd.to_datetime(
        df['NOTA DE RECLAMACAO'], errors='coerce', dayfirst=True
    )

    # Cria a flag HAS_NRT (Se tem data, tem reclamação)
    df['HAS_NRT'] = df['NOTA DE RECLAMACAO'].notna()

    # --- Compatibilidade com os testes: cria coluna underscore como string 'dd/mm/YYYY' ---
    # Mantemos a coluna datetime original ("NOTA DE RECLAMACAO") e criamos a versão formatada.
    formatted = df['NOTA DE RECLAMACAO'].dt.strftime('%d/%m/%Y')
    # Garante que valores NaT virem NaN/pd.NA na coluna string
    formatted.loc[df['NOTA DE RECLAMACAO'].isna()] = pd.NA
    df['NOTA_DE_RECLAMACAO'] = formatted

    # Volta a UC para numérico no final para manter o padrão da base
    df['UC'] = pd.to_numeric(df['UC'], errors='coerce').astype('Int64')

    return df
