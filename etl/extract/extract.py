"""Módulo para extração de dados de arquivos locais."""
from pathlib import Path

import pandas as pd


def load_all_files(input_path: str = 'input'):
    """Lê todos os arquivos da pasta input e retorna um dicionário de DataFrames."""
    path = Path(input_path)

    # Dicionário para guardar nossos DataFrames
    data = {}

    # Mapeamento de arquivos (Nome amigável: Nome do arquivo real)
    files_to_load = {
        'cadastro_consumo': 'CADASTRO E CONSUMO POR UC.csv',
        'medidores': 'MEDIDORES.xlsx',
        'inspecoes': 'INSPECOES.xlsx',
        'ocorrencias': 'OCORRENCIA POR UC.csv',
        'apontamento': 'APONTAMENTO DE LEITURA.csv',
        'codigos_leitura': 'CODIGOS DA LEITURA.xls',
    }

    for key, filename in files_to_load.items():
        file_path = path / filename

        if not file_path.exists():
            raise FileNotFoundError(
                f'Arquivo obrigatório não encontrado: {filename}'
            )

        # Lógica de leitura baseada na extensão
        if file_path.suffix == '.csv':
            data[key] = pd.read_csv(file_path, sep=',', encoding='utf-8')
        elif file_path.suffix in ['.xlsx', '.xls']:
            data[key] = pd.read_excel(file_path)

    return data
