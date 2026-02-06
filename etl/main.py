"""Ponto de entrada principal para o pipeline de ETL."""

import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Dict

from tqdm import tqdm

from etl.extract.extract import load_all_files
from etl.load.load import save_to_csv
from etl.transform.alvos import filter_out_pendentes
from etl.transform.apontamento import (
    enrich_with_apontamento,
    treat_apontamento_codes,
)
from etl.transform.consumo import treat_monthly_consumption
from etl.transform.enriquecimento import enrich_with_new_bases
from etl.transform.inspecoes import enrich_with_inspections
from etl.transform.medidores import enrich_with_medidores
from etl.transform.ocorrencias import enrich_with_occurrences
from etl.transform.regras_negocio import (
    apply_priority_rules,
    calculate_yoy,
    flag_minimum_by_phase,
)

# -----------------------------------------------------------------------------
# Configuração de logs
# -----------------------------------------------------------------------------
LOGS_DIR = Path('logs')
LOGS_DIR.mkdir(exist_ok=True)
LOG_FILE = LOGS_DIR / f"{datetime.now().strftime('%Y-%m-%d')}.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()],
)

# -----------------------------------------------------------------------------
# Regex e toggles
# -----------------------------------------------------------------------------
# Regex para identificar colunas de consumo (MM/YYYY), com ou sem aspas
_MONTH_RE = re.compile(r"^'?(\d{2})/(\d{4})'?$")

# Toggle: remover colunas de consumo mensal do CSV final
# - True: remove (arquivo final sem as colunas de consumo)
# - False: mantém as colunas de consumo no arquivo final
REMOVE_CONSUMO = True

# Toggle: remover colunas técnicas de YoY do CSV final
# - True: remove (arquivo final sem as colunas yoy_)
# - False: mantém as colunas yoy_ no arquivo final
REMOVE_YOY = True


# -----------------------------------------------------------------------------
# Pipeline
# -----------------------------------------------------------------------------
def run_pipeline() -> None:
    """Executa todo o fluxo de ETL com logs e barra de progresso."""
    logging.info('Iniciando Pipeline de ETL...')

    steps = ['Extração', 'Transformação', 'Carga']
    pbar = tqdm(total=len(steps), desc='Progresso Geral')

    try:
        # 1. EXTRAÇÃO
        logging.info('Etapa 1: Extraindo arquivos...')
        data: Dict[str, object] = load_all_files()
        pbar.update(1)

        # 2. TRANSFORMAÇÃO
        logging.info('Etapa 2: Iniciando transformações...')
        df = data['cadastro_consumo']

        # Remove os alvos já abertos pelas outras áreas
        logging.info(
            'Removendo UCs com alvo pendente (CESTA BT - aba PENDENTE)...'
        )
        total_antes = len(df)
        df = filter_out_pendentes(df, data['alvos'])
        total_depois = len(df)
        logging.info(
            'Alvos pendentes removidos: %d (restaram %d)',
            total_antes - total_depois,
            total_depois,
        )

        # Sequência de enriquecimento
        logging.info('Enriquecendo com dados de medidores...')
        df = enrich_with_medidores(df, data['medidores'])

        logging.info('Enriquecendo com dados de inspeções...')
        df = enrich_with_inspections(df, data['inspecoes'])

        logging.info('Enriquecendo com dados de ocorrências...')
        df = enrich_with_occurrences(df, data['ocorrencias'])

        logging.info('Enriquecendo com Sinergia, Seccional e Localização...')
        df = enrich_with_new_bases(df, data)

        # Apontamento (2 passos)
        logging.info('Tratando códigos de apontamento...')
        apontamento_treated = treat_apontamento_codes(
            data['apontamento'], data['codigos_leitura']
        )
        df = enrich_with_apontamento(df, apontamento_treated)

        # Consumo e Regras de Negócio
        logging.info('Tratando consumo mensal...')
        df = treat_monthly_consumption(df)

        logging.info('Calculando YoY (Year over Year)...')
        df = calculate_yoy(df)

        logging.info('Identificando consumo no mínimo da fase...')
        df = flag_minimum_by_phase(df)

        logging.info('Aplicando regras de priorização (P1, P2, P3)...')
        df = apply_priority_rules(df)

        # Identifica colunas yoy_ (técnicas)
        yoy_cols = [c for c in df.columns if c.startswith('yoy_')]
        logging.info('Colunas YoY detectadas: %s', yoy_cols)

        # Se o toggle REMOVE_YOY estiver ativo, removemos essas colunas
        if REMOVE_YOY and yoy_cols:
            logging.info(
                'Removendo %d colunas técnicas (REMOVE_YOY=True)...',
                len(yoy_cols),
            )
            df = df.drop(columns=yoy_cols)
            # limpa a lista para evitar referências posteriores
            yoy_cols = []

        # Filtro: mantém apenas linhas com prioridade definida
        logging.info(
            'Filtrando apenas registros com prioridade (P1, P2, P3)...'
        )
        total_antes = len(df)
        df = df[df['PRIORIDADE'].notna()].copy()
        total_depois = len(df)
        pct = (total_depois / total_antes * 100) if total_antes else 0.0
        logging.info(
            'Filtro aplicado: %d → %d registros (%.1f%% mantidos)',
            total_antes,
            total_depois,
            pct,
        )

        # Identifica colunas de consumo (MM/YYYY)
        consumo_cols = sorted(
            [c for c in df.columns if _MONTH_RE.match(str(c).strip())]
        )
        logging.info('Colunas de consumo detectadas: %s', consumo_cols)

        # Se o toggle REMOVE_CONSUMO estiver ativo, removemos essas colunas
        if REMOVE_CONSUMO and consumo_cols:
            logging.info(
                'Removendo %d colunas de consumo mensal (REMOVE_CONSUMO=True)...',
                len(consumo_cols),
            )
            df = df.drop(columns=consumo_cols)
            consumo_cols = []

        # Reordenação de colunas
        logging.info('Reordenando colunas para o formato final...')
        ordem_final = [
            'UC',
            'STATUS_COMERCIAL',
            'MOVE_IN',
            'MOVE_OUT',
            'GRUPO_TENSAO',
            'CLASSE_PRINCIPAL',
            'CLASSE_CONSUMO',
            'PERIMETRO',
            'SE_AL_NORM',
            'MEDIDOR',
            'ANO',
            'FABRICANTE',
            'FASE',
            'MICRO_GERADOR',
            'INST_MED_FISCAL',
            'ENDERECO',
            'CONDOMINIO',
            'BAIRRO',
            'MUNICIPIO',
            'SECCIONAL',
        ]
        ordem_final += consumo_cols
        ordem_final += [
            'BATE_CAIXA',
            'FISCALIZACAO',
            'COD',
            'NOTA DE RECLAMACAO',
            'LEITURISTA',
            'MEDIA_YOY',
            'NO_MINIMO_4M',
            'PRIORIDADE',
            'MOTIVO_PRIORIDADE',
            'LATITUDE',
            'LONGITUDE',
        ]

        # Garante que só usamos colunas que realmente existem
        colunas_existentes = [c for c in ordem_final if c in df.columns]
        df = df[colunas_existentes]

        logging.info('Colunas finais: %d', len(colunas_existentes))

        pbar.update(1)

        # 3. CARGA
        logging.info('Etapa 3: Exportando para CSV...')
        output_file = save_to_csv(df)
        pbar.update(1)

        logging.info(
            'Pipeline finalizado com sucesso! Arquivo gerado: %s', output_file
        )

    except Exception as exc:
        logging.error('Erro durante a execução do pipeline: %s', exc)
        raise
    finally:
        pbar.close()


if __name__ == '__main__':
    run_pipeline()
