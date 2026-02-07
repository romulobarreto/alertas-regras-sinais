"""Módulo para remover os alvos já abertos pelas outras áreas.

Filtra UCs que já possuem apontamento repetido na base do alertas-regras-sinais.
"""

from __future__ import annotations

from typing import Optional

import pandas as pd


def filter_out_pendentes(
    base_df: pd.DataFrame, alvos_pendentes_df: Optional[pd.DataFrame]
) -> pd.DataFrame:
    """
    Remove UCs que já possuem alvo pendente na CESTA BT (aba PENDENTE).

    A coluna AREA pode existir só como apoio, mas não precisa ir pro output.

    Regras principais:
    - Se `alvos_pendentes_df` for None ou vazio, retorna cópia de base_df.
    - Se a aba não tiver a coluna 'UC', lança KeyError com mensagem esperada
      pelos testes.
    - Não modifica as colunas originais de base_df — só filtra as linhas.
    """
    out = base_df.copy()

    # Validações mínimas
    if 'UC' not in out.columns:
        raise KeyError("A base principal precisa ter a coluna 'UC'.")

    # Se não vier dataframe de alvos, mantemos tudo
    if alvos_pendentes_df is None or alvos_pendentes_df.empty:
        return out

    alvos = alvos_pendentes_df.copy()
    if 'UC' not in alvos.columns:
        raise KeyError(
            "A aba PENDENTES da CESTA BT.xlsx precisa ter a coluna 'UC'."
        )

    # Normaliza UC nos dois lados: tenta converter para numérico (Int64)
    # Valores inválidos viram <NA> e não fazem match.
    base_uc = pd.to_numeric(out['UC'], errors='coerce').astype('Int64')
    alvos_uc = pd.to_numeric(alvos['UC'], errors='coerce').astype('Int64')

    # Set de UCs pendentes (descarta NA)
    pendentes_set = set(alvos_uc.dropna().tolist())

    # Filtra fora (mantém o que NÃO está no conjunto de pendentes)
    mask_keep = ~base_uc.isin(pendentes_set)
    return out.loc[mask_keep].copy()
