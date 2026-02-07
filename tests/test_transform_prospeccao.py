"""Testes para o módulo de prospecção."""
import pandas as pd
import pytest

from etl.transform.prospeccao import enrich_with_prospeccao


def test_enrich_with_prospeccao_ok():
    """Testa se o merge com a base de prospecção traz o dado mais recente."""
    df_cad = pd.DataFrame({'UC': [123, 456]})

    df_pros = pd.DataFrame(
        {
            'UC': [123, 123],
            'DATA': ['2026-01-01', '2026-02-01'],  # 123 tem duas visitas
            'CONCLUSAO': ['INDICIO', 'SEM INDICIO'],
        }
    )

    result = enrich_with_prospeccao(df_cad, df_pros)

    # Deve pegar a data mais recente (2026-02-01)
    uc_123 = result[result['UC'] == 123].iloc[0]
    assert uc_123['CONCLUSAO_PROSPECTOR'] == 'SEM INDICIO'
    assert uc_123['DATA_PROSPECTOR'].month == 2


def test_enrich_with_prospeccao_empty():
    """Testa comportamento com base de prospecção vazia."""
    df_cad = pd.DataFrame({'UC': [123]})
    result = enrich_with_prospeccao(df_cad, None)
    assert 'DATA_PROSPECTOR' in result.columns
    assert pd.isna(result['DATA_PROSPECTOR'].iloc[0])
