"""Testes para o módulo faro_certo."""

import sqlite3
from pathlib import Path

import pandas as pd

input_dir = Path('input')
cadastro_path = input_dir / 'CADASTRO E CONSUMO POR UC.csv'
sqlite_path = input_dir / 'bot_interactions.sqlite'

cadastro = pd.read_csv(cadastro_path, sep=',', encoding='latin-1')
conn = sqlite3.connect(sqlite_path)

# Lê dados do bot (comando 'dados')
df_bot = pd.read_sql_query(
    "SELECT input, timestamp FROM interactions WHERE command = 'dados'", conn
)
conn.close()

# Limpa medidor no cadastro e no bot
cadastro['MEDIDOR_CLEAN'] = cadastro['MEDIDOR'].astype(str).str.strip()
df_bot['MEDIDOR_CLEAN'] = df_bot['input'].astype(str).str.strip()

# Quantidade de medidores únicos em cada base
print(f"Medidores únicos no cadastro: {cadastro['MEDIDOR_CLEAN'].nunique()}")
print(f"Medidores únicos no bot: {df_bot['MEDIDOR_CLEAN'].nunique()}")

# Medidores do bot que aparecem no cadastro
medidores_comuns = set(df_bot['MEDIDOR_CLEAN']).intersection(
    set(cadastro['MEDIDOR_CLEAN'])
)
print(f'Medidores do bot que batem no cadastro: {len(medidores_comuns)}')

# Medidores do bot que NÃO aparecem no cadastro
medidores_fora = set(df_bot['MEDIDOR_CLEAN']).difference(
    set(cadastro['MEDIDOR_CLEAN'])
)
print(f'Medidores do bot que NÃO batem no cadastro: {len(medidores_fora)}')

# Mostrar alguns medidores que não batem (se houver)
if medidores_fora:
    print('Exemplos de medidores do bot que não batem no cadastro:')
    print(list(medidores_fora)[:20])

# Agora, para os medidores que batem, pegar a última data do bot
df_bot['timestamp'] = pd.to_datetime(df_bot['timestamp'], errors='coerce')
df_bot_last = (
    df_bot.groupby('MEDIDOR_CLEAN')['timestamp']
    .max()
    .reset_index()
    .rename(columns={'timestamp': 'FARO_CERTO'})
)

# Merge com cadastro
df_merged = pd.merge(
    cadastro,
    df_bot_last,
    left_on='MEDIDOR_CLEAN',
    right_on='MEDIDOR_CLEAN',
    how='left',
)

# Quantos registros do cadastro receberam data do bot?
print(
    f"Registros do cadastro com data FARO_CERTO: {df_merged['FARO_CERTO'].notna().sum()}"
)
print(
    f"Registros do cadastro sem data FARO_CERTO: {df_merged['FARO_CERTO'].isna().sum()}"
)

# Mostrar algumas linhas com data FARO_CERTO para conferir
print(
    df_merged.loc[
        df_merged['FARO_CERTO'].notna(), ['MEDIDOR', 'FARO_CERTO']
    ].head(10)
)
