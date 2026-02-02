"""Módulo para remover os alvos já abertos pelas outras áreas de um possível apontamento repetido na base do alertas-regras-sinais."""

import pandas as pd


def filter_out_pendentes(
    base_df: pd.DataFrame, alvos_pendentes_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Remove UCs que já possuem alvo pendente na CESTA BT (aba PENDENTE).
    A coluna AREA pode existir só como apoio, mas não precisa ir pro output.
    """
    out = base_df.copy()

    # Normaliza UC nos dois lados
    base_uc = pd.to_numeric(out['UC'], errors='coerce').astype('Int64')

    alvos = alvos_pendentes_df.copy()
    if 'UC' not in alvos.columns:
        raise KeyError(
            "A aba PENDENTES da CESTA BT.xlsx precisa ter a coluna 'UC'."
        )

    alvos_uc = pd.to_numeric(alvos['UC'], errors='coerce').astype('Int64')

    # Set de UCs pendentes
    pendentes_set = set(alvos_uc.dropna().tolist())

    # Filtra fora
    mask_keep = ~base_uc.isin(pendentes_set)
    return out.loc[mask_keep].copy()
