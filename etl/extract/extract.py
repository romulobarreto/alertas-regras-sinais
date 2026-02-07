"""Módulo para extração de dados de arquivos locais."""
import logging
from pathlib import Path
from typing import Dict

import pandas as pd


def load_all_files() -> Dict[str, object]:
    """Carrega todos os arquivos necessários para o pipeline.

    Atenção: o arquivo do Faro Certo (SQLite) é obrigatório.
    Retorna loaded_data com a chave 'faro_sqlite' contendo o caminho absoluto.
    """
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
        'alvos': 'CESTA BT.xlsx',
        'prospeccao': 'PROSPECCAO DE ALVOS.xlsx',  # <-- Nova base
    }

    loaded_data: Dict[str, object] = {}

    for key, filename in files.items():
        path = data_path / filename
        if not path.exists():
            logging.error('Arquivo não encontrado: %s', filename)
            raise FileNotFoundError(f'Arquivo essencial faltando: {filename}')

        logging.info('Carregando %s...', filename)

        if path.suffix.lower() == '.csv':
            try:
                loaded = pd.read_csv(path, sep=';', encoding='latin-1')
                if len(loaded.columns) <= 1:
                    raise ValueError("Leitura com ';' devolveu 1 coluna")
                loaded_data[key] = loaded
            except Exception:
                loaded_data[key] = pd.read_csv(
                    path, sep=',', encoding='latin-1'
                )
        elif path.suffix.lower() in ['.xlsx', '.xls']:
            if key == 'alvos':
                loaded_data[key] = pd.read_excel(path, sheet_name='PENDENTE')
            else:
                loaded_data[key] = pd.read_excel(path)
        else:
            logging.warning(
                'Formato inesperado para %s: %s', filename, path.suffix
            )
            loaded_data[key] = pd.read_csv(path, encoding='latin-1', sep=',')

    # --- Faro Certo (SQLite) — obrigatório ---
    faro_sqlite_path = None
    candidates = ['bot_interactions.sqlite', 'bot_interactions.db']
    for c in candidates:
        p = data_path / c
        if p.exists():
            faro_sqlite_path = p
            break

    if faro_sqlite_path is None and data_path.exists():
        for p in data_path.iterdir():
            if p.suffix.lower() in ['.sqlite', '.db']:
                faro_sqlite_path = p
                logging.info(
                    'Encontrado arquivo sqlite para Faro Certo: %s', p.name
                )
                break

    if not faro_sqlite_path:
        logging.error(
            "Arquivo SQLite do Faro Certo não encontrado em 'input/'. Ele é obrigatório."
        )
        raise FileNotFoundError(
            "Arquivo SQLite do Faro Certo (bot_interactions) é obrigatório e não foi encontrado em 'input/'."
        )

    loaded_data['faro_sqlite'] = str(faro_sqlite_path.resolve())
    logging.info('Faro Certo SQLite detectado: %s', loaded_data['faro_sqlite'])

    return loaded_data
