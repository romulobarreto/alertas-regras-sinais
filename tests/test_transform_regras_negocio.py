"""Testes para o módulo de regras de negócio."""

from datetime import datetime, timedelta

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
    assert abs(result['MEDIA_YOY'].iloc[0] - 0.2) < 1e-6


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
        '02/2026': [100, 100, 100],
    }
    df = pd.DataFrame(data)
    result = flag_minimum_by_phase(df)
    assert all(result['NO_MINIMO_4M'] == 'SIM')


def _create_base_df_with_priority(
    prioridade=None,
    motivo=None,
    status='LG',
    data_prospector=None,
    conclusao_prospector='',
    fabricante='',
    ano=2020,
    fase='MO',
    no_minimo='SIM',
    has_nrt=False,
    media_yoy=0.0,
    cod=None,
    leiturista='',
    move_out=None,
):
    """Helper para criar DataFrame base para testes de prioridade."""
    data = {
        'UC': [1],
        'PRIORIDADE': [prioridade],
        'MOTIVO_PRIORIDADE': [motivo],
        'STATUS_COMERCIAL': [status],
        'DATA_PROSPECTOR': [data_prospector],
        'CONCLUSAO_PROSPECTOR': [conclusao_prospector],
        'FABRICANTE': [fabricante],
        'ANO': [ano],
        'FASE': [fase],
        'NO_MINIMO_4M': [no_minimo],
        'HAS_NRT': [has_nrt],
        'MEDIA_YOY': [media_yoy],
        'COD': [cod],
        'LEITURISTA': [leiturista],
        'MOVE_OUT': [move_out],
    }
    return pd.DataFrame(data)


def test_priority_prospeccao_confirmada():
    """Testa se IRREGULARIDADE CONFIRMADA gera P1."""
    df = _create_base_df_with_priority(
        data_prospector=datetime.now(),
        conclusao_prospector='IRREGULARIDADE CONFIRMADA',
    )
    result = apply_priority_rules(df)
    assert result['PRIORIDADE'].iloc[0] == 'P1'
    assert 'PROSPECCAO' in result['MOTIVO_PRIORIDADE'].iloc[0]


def test_priority_desligado_com_reclamacao():
    """Testa regra P1 para desligado com reclamação após move out."""
    move_out_date = datetime.now() - timedelta(days=10)
    nota_reclamacao_date = move_out_date + timedelta(days=1)

    df = _create_base_df_with_priority(
        status='DS',
        move_out=move_out_date,
        has_nrt=True,
        media_yoy=0.0,
        cod='',
        data_prospector=None,
        conclusao_prospector='',
    )
    df['NOTA_DE_RECLAMACAO'] = [nota_reclamacao_date]

    result = apply_priority_rules(df)
    assert result['PRIORIDADE'].iloc[0] == 'P1'
    assert 'DESLIGADO COM RECLAMAÇÃO' in result['MOTIVO_PRIORIDADE'].iloc[0]


def test_priority_minimo_com_reclamacao():
    """Testa regra P1 para LG com mínimo e reclamação sem esforço recente."""
    df = _create_base_df_with_priority(
        status='LG',
        no_minimo='SIM',
        has_nrt=True,
        media_yoy=0.0,
        data_prospector=None,
        conclusao_prospector='',
    )
    result = apply_priority_rules(df)
    assert result['PRIORIDADE'].iloc[0] == 'P1'
    assert (
        'MÍNIMO DA FASE COM RECLAMAÇÃO' in result['MOTIVO_PRIORIDADE'].iloc[0]
    )


def test_priority_prospeccao_indicio():
    """Testa regra P2 para prospecção com indício e sem esforço."""
    df = _create_base_df_with_priority(
        status='LG',
        data_prospector=None,
        conclusao_prospector='INDICIO DE IRREGULARIDADE',
    )
    result = apply_priority_rules(df)
    assert result['PRIORIDADE'].iloc[0] == 'P2'
    assert 'PROSPECCAO INDICIO' in result['MOTIVO_PRIORIDADE'].iloc[0]


def test_priority_medidor_dowertech_2013():
    """Testa regra P2 para medidor DOWERTECH 2013 no mínimo."""
    df = _create_base_df_with_priority(
        status='LG',
        fabricante='DOWERTECH',
        ano=2013,
        no_minimo='SIM',
    )
    result = apply_priority_rules(df)
    assert result['PRIORIDADE'].iloc[0] == 'P2'
    assert 'DOWERTECH 2013' in result['MOTIVO_PRIORIDADE'].iloc[0]


def test_priority_medidor_antigo():
    """Testa regra P3 para medidor antigo no mínimo."""
    df = _create_base_df_with_priority(
        status='LG',
        ano=1999,
        no_minimo='SIM',
    )
    result = apply_priority_rules(df)
    assert result['PRIORIDADE'].iloc[0] == 'P3'
    assert 'MEDIDOR ANTIGO' in result['MOTIVO_PRIORIDADE'].iloc[0]


def test_priority_condominio_alto_ds():
    """Testa regra P3 para condomínio com alto índice de DS."""
    df = _create_base_df_with_priority(
        status='DS',
        no_minimo='SIM',
    )
    df = pd.concat([df] * 5, ignore_index=True)  # cria 5 linhas
    df['CONDOMINIO'] = ['SIM'] * 5
    df['ENDERECO'] = ['Rua A'] * 5
    result = apply_priority_rules(df)
    # Pelo menos uma linha deve ter prioridade P3
    assert 'P3' in result['PRIORIDADE'].values


def test_priority_queda_acentuada():
    """Testa regra P3 para queda acentuada de consumo."""
    df = _create_base_df_with_priority(
        status='LG',
        media_yoy=-0.5,
        no_minimo='NAO',  # evita conflito com regra consumo no mínimo
    )
    result = apply_priority_rules(df)
    assert result['PRIORIDADE'].iloc[0] == 'P3'
    assert 'QUEDA ACENTUADA' in result['MOTIVO_PRIORIDADE'].iloc[0]
