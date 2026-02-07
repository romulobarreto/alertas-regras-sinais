"""Testes para o módulo faro_certo."""

import sqlite3

import pandas as pd
import pytest

from etl.transform.faro_certo import enrich_with_faro_certo


@pytest.fixture
def mock_sqlite(tmp_path):
    """Cria um banco SQLite temporário para testes."""
    db_path = tmp_path / 'test_bot.sqlite'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    # Criamos com o nome que o teste usa
    cursor.execute(
        'CREATE TABLE bot_interactions (input TEXT, timestamp TEXT, command TEXT)'
    )

    data = [
        ('12345', '2026-01-01 10:00:00', 'dados'),
        ('12345', '2026-01-05 12:00:00', 'dados'),  # Mais recente
        ('99999', '2026-01-02 10:00:00', 'farejar'),
        ('67890', '2026-01-03 08:00:00', 'dados'),
    ]
    cursor.executemany('INSERT INTO bot_interactions VALUES (?, ?, ?)', data)
    conn.commit()
    conn.close()
    return str(db_path)


def test_enrich_with_faro_certo(mock_sqlite):
    # Cadastro fake
    df_cad = pd.DataFrame(
        {'UC': [1, 2, 3], 'MEDIDOR': ['12345', '67890', '11111']}
    )

    result = enrich_with_faro_certo(df_cad, mock_sqlite)

    # Verificações ajustadas para validar a STRING dd/mm/yyyy
    # UC 1 (Medidor 12345) -> 05/01/2026
    assert result.loc[result['UC'] == 1, 'FARO_CERTO'].iloc[0] == '05/01/2026'

    # UC 2 (Medidor 67890) -> 03/01/2026
    assert result.loc[result['UC'] == 2, 'FARO_CERTO'].iloc[0] == '03/01/2026'

    # UC 3 (Medidor 11111) -> Deve ser NaT ou NaN (como o script define no erro/vazio)
    assert pd.isna(result.loc[result['UC'] == 3, 'FARO_CERTO'].iloc[0])
