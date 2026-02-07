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
from etl.transform.faro_certo import enrich_with_faro_certo
from etl.transform.inspecoes import enrich_with_inspections
from etl.transform.medidores import enrich_with_medidores
from etl.transform.ocorrencias import enrich_with_occurrences
from etl.transform.prospeccao import enrich_with_prospeccao
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
_MONTH_RE = re.compile(r"^'?(\d{2})/(\d{4})'?$")

REMOVE_CONSUMO = True
REMOVE_YOY = True
EXPORT_ONLY_PRIORITY = True

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

        logging.info('Removendo UCs com alvo pendente (CESTA BT)...')
        df = filter_out_pendentes(df, data['alvos'])

        logging.info('Enriquecendo com dados de medidores...')
        df = enrich_with_medidores(df, data['medidores'])

        faro_path = data['faro_sqlite']
        logging.info('Enriquecendo com Faro Certo (SQLite): %s', faro_path)
        df = enrich_with_faro_certo(df, faro_path)

        logging.info('Enriquecendo com dados de inspeções...')
        df = enrich_with_inspections(df, data['inspecoes'])

        logging.info('Enriquecendo com dados de ocorrências...')
        df = enrich_with_occurrences(df, data['ocorrencias'])

        # ----- NOVO: Enriquecimento com Prospeccao -----
        logging.info('Enriquecendo com Prospeccao de Alvos (motoca)...')
        df = enrich_with_prospeccao(df, data.get('prospeccao'))
        # ------------------------------------------------

        logging.info('Enriquecendo com Sinergia, Seccional e Localização...')
        df = enrich_with_new_bases(df, data)

        logging.info('Tratando códigos de apontamento...')
        apontamento_treated = treat_apontamento_codes(
            data['apontamento'], data['codigos_leitura']
        )
        df = enrich_with_apontamento(df, apontamento_treated)

        logging.info('Tratando consumo mensal e calculando YoY...')
        df = treat_monthly_consumption(df)
        df = calculate_yoy(df)

        logging.info(
            'Identificando consumo no mínimo e aplicando priorização...'
        )
        df = flag_minimum_by_phase(df)
        df = apply_priority_rules(df)

        if REMOVE_YOY:
            yoy_cols = [c for c in df.columns if c.startswith('yoy_')]
            df = df.drop(columns=yoy_cols)

        if EXPORT_ONLY_PRIORITY:
            df = df[df['PRIORIDADE'].notna()].copy()

        # Limpeza de colunas de consumo mensal
        consumo_cols = sorted(
            [c for c in df.columns if _MONTH_RE.match(str(c).strip())]
        )
        if REMOVE_CONSUMO:
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
            'FARO_CERTO',
            'DATA_PROSPECTOR',
            'CONCLUSAO_PROSPECTOR',
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

        colunas_existentes = [c for c in ordem_final if c in df.columns]
        df = df[colunas_existentes]

        pbar.update(1)

        # 3. CARGA
        logging.info('Etapa 3: Exportando para CSV...')
        output_file = save_to_csv(df)
        pbar.update(1)

        logging.info(f'Pipeline finalizado! Arquivo: {output_file}')

    except Exception as exc:
        logging.error(f'Erro no pipeline: {exc}')
        raise
    finally:
        pbar.close()


if __name__ == '__main__':
    run_pipeline()
