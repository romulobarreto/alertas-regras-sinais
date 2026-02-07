"""Testes para o módulo de regras de negócio."""
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

from etl.transform.regras_negocio import (
    apply_priority_rules,
    calculate_yoy,
    flag_minimum_by_phase,
)


def test_calculate_yoy_ok():
    """Testa se o cálculo de YoY está correto."""
    data = {
        'UC': [1],
        '01/2024': [100],
        '01/2025': [150],
        '02/2024': [200],
        '02/2025': [180],
        '03/2025': [999],  # Mês atual ignorado
    }
    df = pd.DataFrame(data)
    result = calculate_yoy(df)
    assert result['yoy_01_2025'].iloc[0] == 0.5
    assert result['MEDIA_YOY'].iloc[0] == 0.2


def test_priority_prospeccao_confirmada():
    """Testa se IRREGULARIDADE CONFIRMADA gera P1."""
    data = {
        'UC': [1],
        'STATUS_COMERCIAL': ['LG'],
        'DATA_PROSPECTOR': [datetime.now()],
        'CONCLUSAO_PROSPECTOR': ['IRREGULARIDADE CONFIRMADA'],
        'FABRICANTE': [''],
        'ANO': [2020],
        'FASE': ['MO'],
    }
    df = pd.DataFrame(data)
    result = apply_priority_rules(df)
    assert result['PRIORIDADE'].iloc[0] == 'P1'
    assert 'PROSPECCAO' in result['MOTIVO_PRIORIDADE'].iloc[0]


def test_prospeccao_limpa_prioridade():
    """Testa se SEM INDÍCIO impede a priorização de consumo no mínimo."""
    recent_date = datetime.now() - timedelta(days=10)

    data = {
        'UC': [1, 2],
        'STATUS_COMERCIAL': ['LG', 'LG'],
        'NO_MINIMO_4M': ['SIM', 'SIM'],
        'DATA_PROSPECTOR': [pd.NaT, recent_date],
        'CONCLUSAO_PROSPECTOR': ['', 'SEM INDÍCIO DE IRREGULARIDADE'],
        'FABRICANTE': [''],
        'ANO': [2020],
        'FASE': ['MO'],
    }
    df = pd.DataFrame(data)
    result = apply_priority_rules(df)

    # UC 1: Não teve prospecção -> P3 (Consumo no mínimo)
    # UC 2: Teve prospecção "Sem Indício" recente -> Limpa a prioridade
    assert result.loc[result['UC'] == 1, 'PRIORIDADE'].iloc[0] == 'P3'
    assert pd.isna(result.loc[result['UC'] == 2, 'PRIORIDADE'].iloc[0])


def test_flag_minimum_by_phase_ok():
    """Testa se a marcação de mínimo por fase respeita os limites."""
    data = {
        'UC': [1, 2, 3],
        'STATUS_COMERCIAL': ['LG', 'LG', 'LG'],
        'FASE': ['MO', 'BI', 'TR'],
        '10/2025': [30, 50, 100],
        '11/2025': [30, 50, 100],
        '12/2025': [30, 50, 100],
        '01/2026': [30, 50, 100],
        '02/2026': [100, 100, 100],  # Mês atual
    }
    df = pd.DataFrame(data)
    result = flag_minimum_by_phase(df)
    assert all(result['NO_MINIMO_4M'] == 'SIM')
