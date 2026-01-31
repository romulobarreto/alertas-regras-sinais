"""Módulo para carregamento (exportação) dos dados processados."""

from pathlib import Path

import pandas as pd


def save_to_csv(df: pd.DataFrame, output_path: str = 'output'):
    """Salva o CSV formatado para Excel PT-BR (separador ; e decimal ,)."""
    path = Path(output_path)
    path.mkdir(parents=True, exist_ok=True)

    file_name = path / 'CADASTRO_E_CONSUMO_POR_UC_FINAL.csv'

    # decimal=',' faz o 0.106 virar 0,106
    # sep=';' é o padrão que o Excel BR reconhece para abrir colunas direto
    df.to_csv(
        file_name, index=False, sep=';', decimal=',', encoding='utf-8-sig'
    )

    return file_name
