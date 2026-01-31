"""Testes para o módulo de apontamento de leitura."""
import pandas as pd

from etl.transform.apontamento import (
    enrich_with_apontamento,
    treat_apontamento_codes,
)


def test_treat_apontamento_codes_ok():
    """Testa se o merge de códigos traz a descrição corretamente."""
    apontamento = pd.DataFrame(
        {
            'INSTALACAO': [995473803, 64544214],
            'COD_MENS_LEF': [600, 0],
        }
    )
    codigos = pd.DataFrame(
        {
            'Apontamento': [0, 600],
            'Descricao': ['LEITURA NORMAL', 'LEITURA NORMAL'],
        }
    )

    result = treat_apontamento_codes(apontamento, codigos)

    # Ambas devem ter descrição
    assert (
        result.loc[result['INSTALACAO'] == 995473803, 'Descricao'].iloc[0]
        == 'LEITURA NORMAL'
    )
    assert (
        result.loc[result['INSTALACAO'] == 64544214, 'Descricao'].iloc[0]
        == 'LEITURA NORMAL'
    )


def test_enrich_with_apontamento_ok():
    """Testa se o merge com base traz o leiturista corretamente."""
    base = pd.DataFrame({'UC': [995473803, 64544214, 71479945]})
    apontamento = pd.DataFrame(
        {
            'UC': [995473803, 64544214],
            'LEITURISTA': ['LEITURA NORMAL', 'LEITURA NORMAL'],
        }
    )

    result = enrich_with_apontamento(base, apontamento)

    # UC 995473803 tem apontamento
    assert (
        result.loc[result['UC'] == 995473803, 'LEITURISTA'].iloc[0]
        == 'LEITURA NORMAL'
    )
    # UC 71479945 não tem apontamento
    assert pd.isna(result.loc[result['UC'] == 71479945, 'LEITURISTA'].iloc[0])
    # Não perdeu linhas
    assert len(result) == len(base)
