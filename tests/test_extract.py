import pandas as pd
import pytest

from etl.extract.extract import load_all_files


def test_load_all_files_returns_dict():
    # Executa a função
    data = load_all_files()

    # Verifica se é um dicionário
    assert isinstance(data, dict)


def test_check_if_all_keys_exist():
    data = load_all_files()
    expected_keys = [
        'cadastro_consumo',
        'medidores',
        'inspecoes',
        'ocorrencias',
        'apontamento',
        'codigos_leitura',
    ]

    for key in expected_keys:
        assert key in data
        assert isinstance(data[key], pd.DataFrame)


def test_check_if_dataframes_are_not_empty():
    data = load_all_files()
    for key in data:
        assert not data[key].empty, f'O DataFrame {key} está vazio!'
