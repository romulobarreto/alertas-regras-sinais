"""Testes para o módulo de filtro de alvos pendentes."""

import pandas as pd
import pytest

from etl.transform.alvos import filter_out_pendentes


def test_filter_out_pendentes_remove_ucs_corretas():
    """Testa se UCs com alvo pendente são removidas corretamente."""
    # Base de dados principal
    base_df = pd.DataFrame({
        'UC': [5747015, 5828619, 5831946, 9999999, 8888888],
        'STATUS_COMERCIAL': ['LG', 'LG', 'LG', 'LG', 'DS'],
        'MUNICIPIO': ['PELOTAS', 'PELOTAS', 'PELOTAS', 'PELOTAS', 'BAGE']
    })

    # Alvos pendentes (CESTA BT - aba PENDENTES)
    alvos_df = pd.DataFrame({
        'UC': [5747015, 5831946],  # Essas duas têm alvo pendente
        'AREA': ['FISCALIZACAO - LEITURA', 'FISCALIZACAO - LEITURA']
    })

    resultado = filter_out_pendentes(base_df, alvos_df)

    # Deve remover as UCs 5747015 e 5831946
    assert len(resultado) == 3
    assert 5747015 not in resultado['UC'].values
    assert 5831946 not in resultado['UC'].values
    assert 5828619 in resultado['UC'].values
    assert 9999999 in resultado['UC'].values
    assert 8888888 in resultado['UC'].values


def test_filter_out_pendentes_sem_alvos():
    """Testa comportamento quando não há alvos pendentes."""
    base_df = pd.DataFrame({
        'UC': [1111111, 2222222, 3333333],
        'STATUS_COMERCIAL': ['LG', 'LG', 'DS']
    })

    alvos_df = pd.DataFrame({
        'UC': [],
        'AREA': []
    })

    resultado = filter_out_pendentes(base_df, alvos_df)

    # Nenhuma UC deve ser removida
    assert len(resultado) == 3


def test_filter_out_pendentes_todos_pendentes():
    """Testa quando todas as UCs têm alvo pendente."""
    base_df = pd.DataFrame({
        'UC': [5747015, 5828619],
        'STATUS_COMERCIAL': ['LG', 'LG']
    })

    alvos_df = pd.DataFrame({
        'UC': [5747015, 5828619],
        'AREA': ['FISCALIZACAO - LEITURA', 'FISCALIZACAO - DS']
    })

    resultado = filter_out_pendentes(base_df, alvos_df)

    # Todas devem ser removidas
    assert len(resultado) == 0


def test_filter_out_pendentes_uc_com_valores_nulos():
    """Testa tratamento de UCs nulas ou inválidas."""
    base_df = pd.DataFrame({
        'UC': [5747015, None, 'INVALIDO', 5828619],
        'STATUS_COMERCIAL': ['LG', 'LG', 'LG', 'LG']
    })

    alvos_df = pd.DataFrame({
        'UC': [5747015, None],
        'AREA': ['FISCALIZACAO - LEITURA', 'FISCALIZACAO - DS']
    })

    resultado = filter_out_pendentes(base_df, alvos_df)

    # Deve remover apenas a UC 5747015 (válida e pendente)
    # None e INVALIDO não fazem match, então permanecem
    assert len(resultado) == 3  # None, INVALIDO e 5828619 permanecem
    assert 5747015 not in resultado['UC'].values
    assert 5828619 in resultado['UC'].values


def test_filter_out_pendentes_coluna_uc_ausente():
    """Testa erro quando a aba PENDENTES não tem coluna UC."""
    base_df = pd.DataFrame({
        'UC': [5747015, 5828619],
        'STATUS_COMERCIAL': ['LG', 'LG']
    })

    alvos_df = pd.DataFrame({
        'INSTALACAO': [5747015, 5828619],  # Coluna errada
        'AREA': ['FISCALIZACAO - LEITURA', 'FISCALIZACAO - DS']
    })

    with pytest.raises(KeyError, match="A aba PENDENTES da CESTA BT.xlsx precisa ter a coluna 'UC'"):
        filter_out_pendentes(base_df, alvos_df)


def test_filter_out_pendentes_preserva_outras_colunas():
    """Testa se outras colunas são preservadas após o filtro."""
    base_df = pd.DataFrame({
        'UC': [5747015, 5828619, 5831946],
        'STATUS_COMERCIAL': ['LG', 'LG', 'LG'],
        'MUNICIPIO': ['PELOTAS', 'PELOTAS', 'PELOTAS'],
        'PRIORIDADE': ['P1', 'P2', 'P3']
    })

    alvos_df = pd.DataFrame({
        'UC': [5747015],
        'AREA': ['FISCALIZACAO - LEITURA']
    })

    resultado = filter_out_pendentes(base_df, alvos_df)

    # Verifica se as colunas foram preservadas
    assert list(resultado.columns) == ['UC', 'STATUS_COMERCIAL', 'MUNICIPIO', 'PRIORIDADE']
    assert len(resultado) == 2