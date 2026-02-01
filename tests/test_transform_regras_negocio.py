"""Testes para o módulo de regras de negócio."""
import numpy as np
import pandas as pd

from etl.transform.regras_negocio import calculate_yoy, flag_minimum_by_phase


def test_calculate_yoy_ok():
    """Testa se o cálculo de YoY está correto."""
    data = {
        'UC': [1],
        '01/2024': [100],
        '01/2025': [150],
        '02/2024': [200],
        '02/2025': [180],
        '03/2025': [999],  # mês mais recente (atual) -> deve ser ignorado
    }
    df = pd.DataFrame(data)

    result = calculate_yoy(df)
    assert result['yoy_01_2025'].iloc[0] == 0.5  # 50% em decimal
    assert result['yoy_02_2025'].iloc[0] == -0.1   # -10% em decimal
    assert result['MEDIA_YOY'].iloc[0] == 0.2    # 20% em decimal


def test_check_minimum_consumption_ok():
    """Testa se a verificação de mínimo da fase está correta."""
    data = {
        'UC': [1, 2, 3, 4],
        'STATUS_COMERCIAL': ['LG', 'LG', 'LG', 'DS'],
        'FASE': ['MO', 'BI', 'TR', 'MO'],
        '09/2025': [35, 55, 105, 30],
        '10/2025': [38, 58, 108, 32],
        '11/2025': [40, 60, 110, 35],
        '12/2025': [37, 59, 109, 33],
        '01/2026': [100, 100, 100, 100],
    }
    df = pd.DataFrame(data)

    result = flag_minimum_by_phase(df)

    # UC 1: LG + MO + mínimo 35 <= 40 = SIM
    assert result.loc[result['UC'] == 1, 'NO_MINIMO_4M'].iloc[0] == 'SIM'

    # UC 2: LG + BI + mínimo 55 <= 60 = SIM
    assert result.loc[result['UC'] == 2, 'NO_MINIMO_4M'].iloc[0] == 'SIM'

    # UC 3: LG + TR + mínimo 105 <= 110 = SIM
    assert result.loc[result['UC'] == 3, 'NO_MINIMO_4M'].iloc[0] == 'SIM'

    # UC 4: DS (não é LG) = NULL
    assert pd.isna(result.loc[result['UC'] == 4, 'NO_MINIMO_4M'].iloc[0])

def test_priority_rules_with_bate_caixa():
    """Testa se o Bate Caixa impede a priorização (regra dos 4 meses)."""
    from datetime import datetime, timedelta
    today = datetime.now().strftime('%Y-%m-%d')
    recent_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d') # 1 mês atrás
    
    data = {
        'UC': [1, 2],
        'STATUS_COMERCIAL': ['LG', 'LG'],
        'NO_MINIMO_4M': ['SIM', 'SIM'],
        'BATE_CAIXA': [pd.NA, recent_date], # UC 2 já teve bate caixa recente
        'FISCALIZACAO': [pd.NA, pd.NA],
        'FABRICANTE': ['OUTRO', 'OUTRO'],
        'ANO': [2020, 2020]
    }
    df = pd.DataFrame(data)
    
    from etl.transform.regras_negocio import apply_priority_rules
    result = apply_priority_rules(df)
    
    # UC 1 deve ser P3 (Mínimo da fase)
    assert result.loc[result['UC'] == 1, 'PRIORIDADE'].iloc[0] == 'P3'
    
    # UC 2 não deve ter prioridade (Bate Caixa recente impede)
    assert pd.isna(result.loc[result['UC'] == 2, 'PRIORIDADE'].iloc[0])