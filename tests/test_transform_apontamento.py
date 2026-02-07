"""Testes para o módulo de apontamento."""

import pandas as pd
import pytest

from etl.transform.apontamento import (
    enrich_with_apontamento,
    treat_apontamento_codes,
)


def test_treat_apontamento_codes_ok():
    """Testa se a descrição dos códigos é adicionada corretamente."""
    apontamento_df = pd.DataFrame(
        {
            'COD_MENS_LEF': [1, 2, 3, None, 'a'],
            'OUTRA_COL': ['x', 'y', 'z', 'w', 'v'],
        }
    )
    codigos_df = pd.DataFrame(
        {
            'Apontamento': [1, 2, 3],
            'Descricao': ['Desc1', 'Desc2', 'Desc3'],
        }
    )

    result = treat_apontamento_codes(apontamento_df, codigos_df)

    # Verifica se a coluna Descricao foi adicionada e está correta
    assert 'Descricao' in result.columns
    assert (
        result.loc[result['COD_MENS_LEF'] == 1, 'Descricao'].iloc[0] == 'Desc1'
    )
    assert (
        result.loc[result['COD_MENS_LEF'] == 2, 'Descricao'].iloc[0] == 'Desc2'
    )
    assert (
        result.loc[result['COD_MENS_LEF'] == 3, 'Descricao'].iloc[0] == 'Desc3'
    )
    # Valores sem correspondência devem ter NaN
    assert pd.isna(
        result.loc[result['COD_MENS_LEF'].isna(), 'Descricao']
    ).all()
    assert pd.isna(
        result.loc[result['COD_MENS_LEF'] == 'a', 'Descricao']
    ).all()


def test_enrich_with_apontamento_ok():
    """Testa se a base principal é enriquecida com LEITURISTA corretamente."""
    base_df = pd.DataFrame(
        {
            'UC': [10, 20, 30, 40],
            'OUTRA_COL': ['a', 'b', 'c', 'd'],
        }
    )
    apontamento_treated_df = pd.DataFrame(
        {
            'INSTALACAO': [10, 20, 20, 50],
            'Descricao': ['Leit1', 'Leit2', 'Leit2b', 'Leit50'],
        }
    )

    result = enrich_with_apontamento(base_df, apontamento_treated_df)

    # Deve pegar a primeira ocorrência por UC (20 -> 'Leit2')
    assert 'LEITURISTA' in result.columns
    assert result.loc[result['UC'] == 10, 'LEITURISTA'].iloc[0] == 'Leit1'
    assert result.loc[result['UC'] == 20, 'LEITURISTA'].iloc[0] == 'Leit2'
    # UC 30 não tem apontamento -> NaN
    assert pd.isna(result.loc[result['UC'] == 30, 'LEITURISTA']).iloc[0]
    # UC 40 não tem apontamento -> NaN
    assert pd.isna(result.loc[result['UC'] == 40, 'LEITURISTA']).iloc[0]
