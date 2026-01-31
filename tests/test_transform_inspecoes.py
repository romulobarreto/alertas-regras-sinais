"""Testes para o módulo de inspeções."""
import pandas as pd

from etl.transform.inspecoes import enrich_with_inspections


def test_enrich_with_inspections_ok():
    """Testa se o merge de inspeções traz a data e o código corretamente."""
    base = pd.DataFrame({'UC': [10, 20]})
    inspections = pd.DataFrame(
        {
            'UC / MD': [10, 10],
            'DATA_EXECUCAO': ['2026-01-01', '2026-01-29'],
            'COD': [300, 311],
        }
    )

    result = enrich_with_inspections(base, inspections)

    # Deve trazer a inspeção mais recente (2026-01-29) para a UC 10
    assert result.loc[result['UC'] == 10, 'COD'].iloc[0] == 311
    # UC 20 não tem inspeção, deve ser NaN
    assert pd.isna(result.loc[result['UC'] == 20, 'COD'].iloc[0])
