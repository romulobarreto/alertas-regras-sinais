"""Ponto de entrada principal para o pipeline de ETL."""
import logging
import re
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
from etl.transform.enriquecimento import enrich_with_new_bases
from etl.transform.inspecoes import enrich_with_inspections
from etl.transform.medidores import enrich_with_medidores
from etl.transform.ocorrencias import enrich_with_occurrences
from etl.transform.regras_negocio import (
    apply_priority_rules,
    calculate_yoy,
    flag_minimum_by_phase,
)

# Configuração de Log
log_path = Path('logs')
log_path.mkdir(exist_ok=True)
log_file = log_path / f"{datetime.now().strftime('%Y-%m-%d')}.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler(log_file), logging.StreamHandler()],
)

# Regex para identificar colunas de consumo (MM/YYYY)
_MONTH_RE = re.compile(r"^'?(\d{2})/(\d{4})'?$")


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

        # Remove colunas técnicas (yoy_...)
        yoy_cols = [c for c in df.columns if c.startswith('yoy_')]
        if yoy_cols:
            logging.info(
                f'Removendo {len(yoy_cols)} colunas técnicas (yoy_)...'
            )
            df = df.drop(columns=yoy_cols)

        # Filtro: mantém apenas linhas com prioridade definida
        logging.info(
            'Filtrando apenas registros com prioridade (P1, P2, P3)...'
        )
        total_antes = len(df)
        df = df[df['PRIORIDADE'].notna()].copy()
        total_depois = len(df)
        logging.info(
            f'Filtro aplicado: {total_antes} → {total_depois} registros '
            f'({total_depois / total_antes * 100:.1f}% mantidos)'
        )

        # Reordenação de colunas
        logging.info('Reordenando colunas para o formato final...')
        consumo_cols = sorted(
            [c for c in df.columns if _MONTH_RE.match(str(c).strip())]
        )

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

        logging.info(f'Colunas finais: {len(colunas_existentes)}')

        pbar.update(1)

        # 3. CARGA
        logging.info('Etapa 3: Exportando para CSV...')
        output_file = save_to_csv(df)

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
