"""Testes para o módulo de ocorrências."""
import pandas as pd

from etl.transform.ocorrencias import enrich_with_occurrences


def test_enrich_with_occurrences_ok():
    """Testa se o merge de ocorrências traz a data corretamente."""
    base = pd.DataFrame({'UC': [67187897, 1006523798, 62248723]})
    occurrences = pd.DataFrame(
        {
            'CR_NUMERO': [67187897, 1006523798],
            'OCO_DATA_NR': ['30/01/2026', '30/01/2026'],
        }
    )

    result = enrich_with_occurrences(base, occurrences)

    # UC 67187897 tem ocorrência
    assert (
        result.loc[result['UC'] == 67187897, 'NOTA_DE_RECLAMACAO'].iloc[0]
        == '30/01/2026'
    )
    # UC 62248723 não tem ocorrência
    assert pd.isna(
        result.loc[result['UC'] == 62248723, 'NOTA_DE_RECLAMACAO'].iloc[0]
    )
    # Não perdeu linhas
    assert len(result) == len(base)
