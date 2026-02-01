"""Testes para o módulo de enriquecimento de dados."""
import pandas as pd

from etl.transform.enriquecimento import enrich_with_new_bases


def test_enrich_new_bases():
    df_mock = pd.DataFrame({'UC': [123], 'MUNICIPIO': ['PELOTAS']})
    data_mock = {
        'sinergia': pd.DataFrame(
            {'number': [123], 'timestamp': ['2026-01-30 10:00:00']}
        ),
        'seccional': pd.DataFrame(
            {'MUNICIPIO': ['PELOTAS'], 'SECCCIONAL': ['SUL']}
        ),
        'localizacao': pd.DataFrame(
            {
                'uc': [123],
                'classe_consumo': ['RESIDENCIAL'],
                'latitude': [-31.7],
                'longitude': [-52.3],
            }
        ),
    }

    result = enrich_with_new_bases(df_mock, data_mock)
    assert 'BATE_CAIXA' in result.columns
    assert result.iloc[0]['SECCIONAL'] == 'SUL'
    assert result.iloc[0]['CLASSE_CONSUMO'] == 'RESIDENCIAL'
    print('Teste de Enriquecimento: OK!')
