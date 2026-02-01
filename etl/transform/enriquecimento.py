"""Módulo para enriquecimento de dados de bate caixa, seccional, latitude e longitude."""
import pandas as pd


def enrich_with_new_bases(df: pd.DataFrame, data: dict) -> pd.DataFrame:
    """Adiciona Bate Caixa, Seccional, Classe Consumo e Coordenadas."""
    out = df.copy()

    # 1. Bate Caixa (Sinergia)
    # Pegamos a UC (number) e a data (timestamp)
    sinergia = data['sinergia'].copy()
    sinergia['timestamp'] = pd.to_datetime(sinergia['timestamp']).dt.date
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
    out = out.merge(
        seccional[['MUNICIPIO', 'SECCCIONAL']], on='MUNICIPIO', how='left'
    ).rename(columns={'SECCCIONAL': 'SECCIONAL'})

    # 3. Localização e Tipo Cliente
    loc = data['localizacao'].copy()
    
    # Garante que UC seja tratada como número para o merge
    loc['uc'] = pd.to_numeric(loc['uc'], errors='coerce')
    out['UC'] = pd.to_numeric(out['UC'], errors='coerce')

    # --- TRATAMENTO DE LAT/LONG PARA EXCEL ---
    for col in ['latitude', 'longitude']:
        # 1. Converte para string e troca vírgula por ponto
        loc[col] = loc[col].astype(str).str.replace(',', '.')
        # 2. Converte para numérico
        loc[col] = pd.to_numeric(loc[col], errors='coerce')
        # 3. Se o número for maior que 100 ou menor que -100, é porque está sem o ponto decimal
        # Ex: -3133742773 vira -31.33742773
        mask = (loc[col] > 100) | (loc[col] < -100)
        # Dividimos por 10^8 ou 10^7 dependendo do tamanho, mas o padrão de lat/long costuma ser 2 casas antes do ponto
        # Uma forma segura é garantir que o número fique entre -180 e 180
        while loc.loc[mask, col].abs().max() > 180:
            loc.loc[mask, col] = loc.loc[mask, col] / 10

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
