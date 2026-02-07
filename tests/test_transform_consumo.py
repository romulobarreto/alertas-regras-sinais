"""Testes para o módulo de consumo mensal."""
import pandas as pd
import pandas.api.types as ptypes

from etl.transform.consumo import treat_monthly_consumption


def test_treat_monthly_consumption_basic():
    df = pd.DataFrame(
        {
            'UC': [1, 2, 3],
            '01/2024': [None, '10', 5],
            'OUTRA': ['x', 'y', 'z'],
        }
    )

    out = treat_monthly_consumption(df)

    assert list(out['01/2024']) == [0, 10, 5]
    assert out['OUTRA'].tolist() == ['x', 'y', 'z']
    assert ptypes.is_integer_dtype(out['01/2024'].dtype)


def test_treat_monthly_consumption_quoted_column():
    df = pd.DataFrame(
        {
            'UC': [1, 2],
            "'02/2024'": ['3', None],
            '"03/2024"': [
                4,
                '2',
            ],  # coluna com aspas duplas não é removida pelo strip("'"), deve ser ignorada
        }
    )

    out = treat_monthly_consumption(df)

    # "'02/2024'" deve ser detectada e convertida
    assert list(out["'02/2024'"]) == [3, 0]
    assert ptypes.is_integer_dtype(out["'02/2024'"].dtype)
    # '"03/2024"' não corresponde ao padrão após strip("'"), logo deve ser ignorada e permanecer como estava
    assert out['"03/2024"'].tolist() == [4, '2']


def test_treat_monthly_consumption_ignores_non_matching():
    df = pd.DataFrame(
        {
            'UC': [1],
            '1/2024': ['10'],  # formato inválido (não tem 2 dígitos no mês)
            'MM/YYYY': ['20'],  # formato inválido
            '04/2024 ': [
                '30'
            ],  # com espaço no final -> strip resolve e deve ser aceito
        }
    )

    out = treat_monthly_consumption(df)

    # '1/2024' e 'MM/YYYY' não devem ser convertidas
    assert out['1/2024'].iloc[0] == '10'
    assert out['MM/YYYY'].iloc[0] == '20'
    # '04/2024 ' com espaço deve ser tratado como '04/2024'
    assert out['04/2024 '].iloc[0] == 30
    assert ptypes.is_integer_dtype(out['04/2024 '].dtype)


def test_treat_monthly_consumption_handles_decimals_and_invalids():
    df = pd.DataFrame(
        {
            '01/2024': ['2.9', 'abc', None, 5.7],
        }
    )

    out = treat_monthly_consumption(df)

    # '2.9' -> 2 (astype(int) trunca), 'abc' -> NaN -> 0, None -> 0, 5.7 -> 5
    assert list(out['01/2024']) == [2, 0, 0, 5]
