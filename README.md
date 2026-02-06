# ⚡ Alertas, Regras e Sinais — Recuperação de Energia (CEEE Equatorial)

> Direcionamento inteligente de inspeções a partir de dados (faturamento, histórico, apontamentos e esforço de campo).

[![Python](https://img.shields.io/badge/Python-3.12-2E3079?logo=python&logoColor=white)](https://www.python.org/)
[![Poetry](https://img.shields.io/badge/Poetry-Enabled-6763AC?logo=poetry&logoColor=white)](https://python-poetry.org/)
[![MkDocs](https://img.shields.io/badge/Docs-MkDocs%20Material-0A4780?logo=materialformkdocs&logoColor=white)](https://squidfunk.github.io/mkdocs-material/)

## 🚀 Por que esse projeto existe?

No setor de **Recuperação de Energia**, a gente convive com uma dor bem real: **falta uma bússola**.

Hoje, muitas vezes, a equipe precisa escolher “no feeling” uma região/rua e fazer o famoso **bate-caixa** (pré-inspeção) medidor por medidor — o que consome tempo, combustível e energia da equipe.

Este projeto nasceu para **trocar aleatoriedade por evidência**.

✅ Em vez de procurar problema no escuro, a gente usa dados para apontar **onde a chance de irregularidade/defeito e perda de energia é maior**.

## 🎯 O que ele entrega?

- **Priorização automática** em **P1, P2 e P3**
- **Filtro de esforço (4–6 meses)**: evita re-bater em locais com fiscalização/bate-caixa recente
- **Sinais de consumo** (YoY e mínimo da fase)
- **Apontamentos do leiturista** como sinal de suspeita
- **Geolocalização** (latitude/longitude) pronta para rotas e mapas
- **Visão para dias de chuva**: condomínios com alto índice de `DS`

## 🧠 Matriz de Priorização (resumo)

> A lógica completa (com detalhes) está na documentação do projeto.

| Prioridade | Regra | Resumo da lógica |
|---|---|---|
| **P1** 🚨 | Desligado com Reclamação | `DS` + tem reclamação (após move-out)+ **sem** visita após move-out |
| **P1** 🚨 | Mínimo da Fase com Reclamação | `LG` + mínimo (4m) + reclamação + **sem** visita (4m) |
| **P2** ⚠️ | Reincidente com Queda | `LG` + fraude histórica + YoY ≤ -40% + **sem** visita (6m) |
| **P2** ⚠️ | Mínimo com Apontamento Suspeito | `LG` + mínimo + apontamento relevante + **sem** visita (4m) |
| **P2** ⚠️ | Dowertech 2013, 2014 no Mínimo | fabricante `DOWERTECH` + ano 2014 + `LG` + mínimo + **sem** visita (4m) |
| **P3** 🔎 | Medidor Antigo no Mínimo | ano <= 2000 + `LG` + mínimo + **sem** visita (4m) |
| **P3** 🔎 | Condomínio com Alto DS | condomínio com **>= 5 UCs** em `DS` no mesmo endereço |
| **P3** 🔎 | Desligado Recente + Fraude | `DS` (6m) + fraude histórica + **sem** visita após move-out |
| **P3** 🔎 | Consumo no Mínimo | `LG` + mínimo (4m) + **sem** visita (4m) |
| **P3** 🔎 | Queda Acentuada | `LG` + YoY ≤ -40% + **sem** visita (6m) |

`Desconsiderar alvos já abertos`

**Alvos que já estão abertos por outras áreas** são removidos do conjunto de priorização, evitando retrabalho e duplicidade de atuação.

## 🗂️ Dados de entrada (input)

O pipeline espera estes arquivos dentro da pasta `input/` (nomes exatos):

- `CADASTRO E CONSUMO POR UC.csv`
- `CESTA BT.xlsx`
- `MEDIDORES.xlsx`
- `INSPECOES.xlsx`
- `OCORRENCIA POR UC.csv`
- `APONTAMENTO DE LEITURA.csv`
- `CODIGOS DA LEITURA.xls`
- `SINERGIA.csv`
- `SECCIONAL.csv`
- `LOCALIZACAO E TIPO CLIENTE.csv`

## 📦 Saída (output)

Ao final, é gerado um CSV pronto para uso no Excel/Power BI:

- `output/DIRECIONAMENTO_FINAL.csv`

Ele já sai com:
- `PRIORIDADE` e `MOTIVO_PRIORIDADE`
- `MEDIA_YOY` (decimal, pronto pra formatar como % no Excel)
- `LATITUDE` e `LONGITUDE`
- `BATE_CAIXA`, `FISCALIZACAO` e `NOTA DE RECLAMAÇÃO` (quando existirem).

## 🛠️ Como rodar (dev)

### 1) Clonar

```bash
git clone https://github.com/romulobarreto/alertas-regras-sinais.git
cd alertas-regras-sinais
```

### 2) Ambiente (Poetry + Python 3.12)

```bash
poetry env use python3.12
poetry install
```

Ativar a venv:

```bash
# Mac/Linux
source .venv/bin/activate

# Windows (PowerShell)
# .venv\Scripts\Activate.ps1
```

### 3) Preparar pastas

Crie:

- `input/` (coloque os arquivos de entrada)
- `output/` (onde o relatório final será salvo)

### 4) Executar

```bash
task run
```

## 📚 Documentação

A documentação do projeto fica no site gerado com MkDocs.

- Se você estiver rodando localmente: `mkdocs serve`
- Se estiver publicado via GitHub Pages: confira a aba “Deployments” do repositório

## 🧩 Stack

- **Python 3.12**
- **Pandas / NumPy**
- **Taskipy** (execução simples: `task run`)
- **Pytest** (testes)
- **MkDocs Material** (documentação)

## ✅ Testes

```bash
pytest -q
```

## 🧠 Ideias de próximos passos (fork)

- 🗺️ **Streamlit** com mapa (clusters por seccional/município)
- 📍 Sugestão automática de rotas por proximidade
- 📈 Métricas de acurácia (recuperação/inspeção) por regra
- 🔄 Integração com fontes oficiais (quando disponível)

## 🤝 Contribuição

Se tu for do time e quiser melhorar algo:

1. Abre uma issue com a ideia
2. Cria uma branch
3. Manda PR

---

Feito com energia por Rômulo Barreto da Silva - Analista de Distribuição ⚡
