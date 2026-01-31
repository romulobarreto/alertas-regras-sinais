"""Ponto de entrada principal para o pipeline de ETL."""
import logging
from datetime import datetime
from pathlib import Path

from tqdm import tqdm

from etl.extract.extract import load_all_files
from etl.load.load import save_to_csv
from etl.transform.apontamento import (
    enrich_with_apontamento,
    treat_apontamento_codes,
)
from etl.transform.consumo import treat_monthly_consumption
from etl.transform.inspecoes import enrich_with_inspections
from etl.transform.medidores import enrich_with_medidores
from etl.transform.ocorrencias import enrich_with_occurrences
from etl.transform.regras_negocio import calculate_yoy, flag_minimum_by_phase

# Configuração de Log
log_path = Path('logs')
log_path.mkdir(exist_ok=True)
log_file = log_path / f"{datetime.now().strftime('%Y-%m-%d')}.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler(log_file), logging.StreamHandler()],
)


def run_pipeline():
    """Executa todo o fluxo de ETL com logs e barra de progresso."""
    logging.info('Iniciando Pipeline de ETL...')

    steps = ['Extração', 'Transformação', 'Carga']
    pbar = tqdm(total=len(steps), desc='Progresso Geral')

    try:
        # 1. EXTRAÇÃO
        logging.info('Etapa 1: Extraindo arquivos...')
        data = load_all_files()
        pbar.update(1)

        # 2. TRANSFORMAÇÃO
        logging.info('Etapa 2: Iniciando transformações...')
        df = data['cadastro_consumo']

        # Sequência de enriquecimento
        df = enrich_with_medidores(df, data['medidores'])
        df = enrich_with_inspections(df, data['inspecoes'])
        df = enrich_with_occurrences(df, data['ocorrencias'])

        # Apontamento (2 passos)
        apontamento_treated = treat_apontamento_codes(
            data['apontamento'], data['codigos_leitura']
        )
        df = enrich_with_apontamento(df, apontamento_treated)

        # Consumo
        df = treat_monthly_consumption(df)
        df = calculate_yoy(df)

        # remover colunas yoy do dataframe final
        yoy_cols = [c for c in df.columns if c.startswith('yoy_')]
        df = df.drop(columns=yoy_cols)
        df = flag_minimum_by_phase(df)

        pbar.update(1)

        # 3. CARGA
        logging.info('Etapa 3: Exportando para Excel...')
        output_file = save_to_csv(df)
        pbar.update(1)

        logging.info(
            f'Pipeline finalizado com sucesso! Arquivo gerado: {output_file}'
        )

    except Exception as e:
        logging.error(f'Erro durante a execução do pipeline: {e}')
        raise
    finally:
        pbar.close()


if __name__ == '__main__':
    run_pipeline()
