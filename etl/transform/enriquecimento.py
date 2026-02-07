"""Módulo para enriquecimento de dados de bate caixa, seccional, latitude e longitude."""
from __future__ import annotations

from typing import Dict

import pandas as pd


def enrich_with_new_bases(
    df: pd.DataFrame, data: Dict[str, pd.DataFrame]
) -> pd.DataFrame:
    """Adiciona BATE_CAIXA, SECCIONAL, CLASSE_CONSUMO, LATITUDE e LONGITUDE ao DataFrame.

    Mantém o comportamento original, apenas adiciona checagens e robustez em tipos.
    """
    out = df.copy()

    # Valida presença das bases esperadas
    for key in ('sinergia', 'seccional', 'localizacao'):
        if key not in data:
            raise KeyError(f"A chave '{key}' precisa existir no dict data.")

    # 1. Bate Caixa (Sinergia)
    sinergia = data['sinergia'].copy()
    # Garante tipos coerentes
    if 'number' not in sinergia.columns or 'timestamp' not in sinergia.columns:
        raise KeyError(
            "A tabela 'sinergia' precisa ter as colunas 'number' e 'timestamp'."
        )

    sinergia['number'] = pd.to_numeric(sinergia['number'], errors='coerce')
    # Parse seguro da timestamp; keep apenas a data
    sinergia['timestamp'] = pd.to_datetime(
        sinergia['timestamp'], errors='coerce'
    ).dt.date
    # Se houver duplicatas de UC no Sinergia, pegamos a data mais recente
    sinergia = sinergia.sort_values('timestamp').drop_duplicates(
        'number', keep='last'
    )

    out = (
        out.merge(
            sinergia[['number', 'timestamp']],
            left_on='UC',
            right_on='number',
            how='left',
        )
        .rename(columns={'timestamp': 'BATE_CAIXA'})
        .drop(columns=['number'])
    )

    # 2. Seccional
    seccional = data['seccional'].copy()
    if 'MUNICIPIO' not in seccional.columns:
        raise KeyError(
            "A tabela 'seccional' precisa ter a coluna 'MUNICIPIO'."
        )
    # mantém nome original 'SECCCIONAL' vindo da fonte, renomeia para SECCIONAL no resultado
    if 'SECCCIONAL' not in seccional.columns:
        raise KeyError(
            "A tabela 'seccional' precisa ter a coluna 'SECCCIONAL' (origem)."
        )

    out = out.merge(
        seccional[['MUNICIPIO', 'SECCCIONAL']],
        on='MUNICIPIO',
        how='left',
    ).rename(columns={'SECCCIONAL': 'SECCIONAL'})

    # 3. Localização e Tipo Cliente
    loc = data['localizacao'].copy()
    for required in ('uc', 'classe_consumo', 'latitude', 'longitude'):
        if required not in loc.columns:
            raise KeyError(
                f"A tabela 'localizacao' precisa ter a coluna '{required}'."
            )

    # Garante que UC seja tratado como número para o merge
    loc['uc'] = pd.to_numeric(loc['uc'], errors='coerce')
    out['UC'] = pd.to_numeric(out['UC'], errors='coerce')

    # --- TRATAMENTO DE LAT/LONG PARA EXCEL ---
    for col in ('latitude', 'longitude'):
        # 1. Converte para string e troca vírgula por ponto (regex=False para evitar warning)
        loc[col] = loc[col].astype(str).str.replace(',', '.', regex=False)
        # 2. Converte para numérico
        loc[col] = pd.to_numeric(loc[col], errors='coerce')
        # 3. Ajusta valores muito grandes (sem ponto decimal). Divide por 10 até cair em intervalo [-180, 180].
        mask = loc[col].abs() > 180
        # Evita erro se não houver valores que satisfaçam a máscara
        if mask.any():
            # Enquanto houver valores fora do intervalo, divide por 10
            while True:
                sub = loc.loc[mask, col].abs()
                if sub.empty or sub.max() <= 180:
                    break
                loc.loc[mask, col] = loc.loc[mask, col] / 10
                mask = loc[col].abs() > 180

    out = (
        out.merge(
            loc[['uc', 'classe_consumo', 'latitude', 'longitude']],
            left_on='UC',
            right_on='uc',
            how='left',
        )
        .rename(
            columns={
                'classe_consumo': 'CLASSE_CONSUMO',
                'latitude': 'LATITUDE',
                'longitude': 'LONGITUDE',
            }
        )
        .drop(columns=['uc'])
    )

    return out
