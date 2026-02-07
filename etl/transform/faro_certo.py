"""Módulo para processamento de dados do bot Telegram (Faro Certo)."""

import logging
import sqlite3
from pathlib import Path
from typing import List, Optional

import pandas as pd


def _find_col(cols: List[str], candidates: List[str]) -> Optional[str]:
    """Encontra coluna em cols que contenha qualquer candidato (case-insensitive)."""
    lower = [c.lower() for c in cols]
    for cand in candidates:
        for i, col in enumerate(lower):
            if cand in col:
                return cols[i]
    return None


def enrich_with_faro_certo(
    df_cadastro: pd.DataFrame, sqlite_path: str
) -> pd.DataFrame:
    """Enriquece o cadastro com a data da última consulta no bot Faro Certo."""
    sqlite_file = Path(sqlite_path)
    if not sqlite_file.exists():
        logging.error('Arquivo SQLite não encontrado: %s', sqlite_path)
        df_cadastro['FARO_CERTO'] = pd.NaT
        return df_cadastro

    try:
        with sqlite3.connect(sqlite_path) as conn:
            df_bot = pd.read_sql_query('SELECT * FROM interactions', conn)

        if df_bot.empty:
            df_cadastro['FARO_CERTO'] = pd.NaT
            return df_cadastro

        cols = list(df_bot.columns)
        medidor_col = _find_col(
            cols, ['input', 'medidor', 'meter', 'text', 'message']
        )
        ts_col = _find_col(
            cols, ['timestamp', 'created_at', 'created', 'time', 'ts', 'date']
        )
        cmd_col = _find_col(
            cols, ['command', 'cmd', 'action', 'type', 'event']
        )

        if not medidor_col or not ts_col:
            df_cadastro['FARO_CERTO'] = pd.NaT
            return df_cadastro

        # Filtra apenas comando 'dados'
        if cmd_col:
            df_bot = df_bot[
                df_bot[cmd_col].astype(str).str.strip().str.lower() == 'dados'
            ].copy()

        # Converte timestamp para datetime (formato ISO, sem dayfirst)
        df_bot['TS_PARSED'] = pd.to_datetime(df_bot[ts_col], errors='coerce')

        # Remove linhas com timestamp inválido
        df_bot = df_bot[df_bot['TS_PARSED'].notna()].copy()

        # Extrai dia, mês e ano
        df_bot['DIA'] = df_bot['TS_PARSED'].dt.day.astype(str).str.zfill(2)
        df_bot['MES'] = df_bot['TS_PARSED'].dt.month.astype(str).str.zfill(2)
        df_bot['ANO'] = df_bot['TS_PARSED'].dt.year.astype(str)

        # Monta a data no formato dd/mm/yyyy
        df_bot['FARO_CERTO'] = (
            df_bot['DIA'] + '/' + df_bot['MES'] + '/' + df_bot['ANO']
        )

        # Pega a última interação por medidor, usando a data original para ordenar
        df_bot['MEDIDOR_BOT'] = (
            df_bot[medidor_col].astype(str).str.strip().str.upper()
        )
        df_last = (
            df_bot.sort_values('TS_PARSED')
            .groupby('MEDIDOR_BOT')
            .last()
            .reset_index()
        )

        # Mantém só as colunas necessárias
        df_last = df_last[['MEDIDOR_BOT', 'FARO_CERTO']]
        df_last.columns = ['MEDIDOR_JOIN', 'FARO_CERTO']

        # Merge com cadastro
        df_cadastro['MEDIDOR_CLEAN'] = (
            df_cadastro['MEDIDOR'].astype(str).str.strip().str.upper()
        )
        out = pd.merge(
            df_cadastro,
            df_last,
            left_on='MEDIDOR_CLEAN',
            right_on='MEDIDOR_JOIN',
            how='left',
        )

        return out.drop(columns=['MEDIDOR_JOIN', 'MEDIDOR_CLEAN'])

    except Exception as exc:
        logging.error('Erro Faro Certo: %s', exc)
        df_cadastro['FARO_CERTO'] = pd.NaT
        return df_cadastro
