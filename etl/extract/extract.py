"""Módulo para extração de dados de arquivos locais."""
import logging
from pathlib import Path

import pandas as pd


def load_all_files():
    """Carrega todos os arquivos necessários para o pipeline."""
    data_path = Path('input')

    files = {
        'cadastro_consumo': 'CADASTRO E CONSUMO POR UC.csv',
        'medidores': 'MEDIDORES.xlsx',
        'inspecoes': 'INSPECOES.xlsx',
        'ocorrencias': 'OCORRENCIA POR UC.csv',
        'apontamento': 'APONTAMENTO DE LEITURA.csv',
        'codigos_leitura': 'CODIGOS DA LEITURA.xls',
        'sinergia': 'SINERGIA.csv',
        'seccional': 'SECCIONAL.csv',
        'localizacao': 'LOCALIZACAO E TIPO CLIENTE.csv',
    }

    loaded_data = {}

    for key, filename in files.items():
        path = data_path / filename
        if not path.exists():
            logging.error(f'Arquivo não encontrado: {filename}')
            raise FileNotFoundError(f'Arquivo essencial faltando: {filename}')

        logging.info(f'Carregando {filename}...')

        if path.suffix == '.csv':
            # Tenta ler com ponto e vírgula, se falhar tenta vírgula
            try:
                loaded_data[key] = pd.read_csv(
                    path, sep=';', encoding='latin-1'
                )
                if (
                    len(loaded_data[key].columns) <= 1
                ):   # Se leu errado, só terá 1 coluna
                    raise ValueError
            except:
                loaded_data[key] = pd.read_csv(
                    path, sep=',', encoding='latin-1'
                )
        elif path.suffix in ['.xlsx', '.xls']:
            loaded_data[key] = pd.read_excel(path)

    return loaded_data
