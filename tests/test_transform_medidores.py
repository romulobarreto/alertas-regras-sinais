import pandas as pd

from etl.transform.medidores import enrich_with_medidores


def test_enrich_with_medidores_procv_ok():
    base = pd.DataFrame(
        {
            'UC': [1, 2, 3],
            'MEDIDOR': [100, 200, 300],
        }
    )

    medidores = pd.DataFrame(
        {
            'medidor': [100, 200],
            'ANO': [2020, 2021],
            'FABRICANTE': ['NANSEN', 'ELETRA'],
        }
    )

    result = enrich_with_medidores(base, medidores)

    # UC 1 → encontrou
    assert result.loc[result['UC'] == 1, 'ANO'].iloc[0] == 2020
    assert result.loc[result['UC'] == 1, 'FABRICANTE'].iloc[0] == 'NANSEN'

    # UC 3 → não encontrou
    assert pd.isna(result.loc[result['UC'] == 3, 'ANO'].iloc[0])
    assert pd.isna(result.loc[result['UC'] == 3, 'FABRICANTE'].iloc[0])

    # Garantir que não perdeu linhas
    assert len(result) == len(base)
