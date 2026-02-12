# 🛠️ Guia de Execução

Siga os passos abaixo para configurar o ambiente, preparar os dados e rodar o pipeline de inteligência.

### 1. Clonar o Repositório
Primeiro, traga o projeto para sua máquina local utilizando o Git:

```bash
git clone https://github.com/romulobarreto/alertas-regras-sinais.git
cd alertas-regras-sinais
```

### 2. Configurar o Ambiente Virtual
Este projeto utiliza o **Poetry** para gerenciamento de dependências e o **Python 3.12**.

```bash
# Definir a versão do Python e criar o ambiente
poetry env use python3.12

# Ativar o ambiente virtual (.venv)
# No Mac/Linux:
source .venv/bin/activate
# No Windows:
# .venv\Scripts\activate

# Instalar todas as dependências necessárias
poetry install
```

### 3. Preparação das Pastas e Dados
O sistema trabalha com uma estrutura de pastas rígida para garantir a organização. Certifique-se de que as pastas `input/` e `output/` existam na raiz do projeto.

1. Crie a pasta `input/` caso ela não exista.
2. Insira as planilhas de dados brutos dentro da pasta `input/`. Os arquivos esperados são:
   * `APONTAMENTO DE LEITURA.csv`
   * `BOT_INTERACTIONS.sqlite`
   * `CADASTRO E CONSUMO POR UC.csv`
   * `CESTA BT.xlsx`
   * `CODIGOS DA LEITURA.xls`
   * `INSPECOES.xlsx`
   * `LOCALIZACAO E TIPO CLIENTE.csv`
   * `MEDIDORES.xlsx`
   * `OCORRENCIA POR UC.csv`
   * `SECCIONAL.csv`
   * `SINERGIA.csv`
   

### 4. Execução do Pipeline 🚀
Para facilitar o dia a dia, utilizamos o **taskipy**. Você não precisa decorar comandos longos, basta rodar:

```bash
task run
```

O que este comando faz por baixo dos panos:
* Limpa logs antigos.
* Inicia a extração dos dados.
* Aplica as transformações e enriquecimentos.
* Executa a **Matriz de Priorização (P1, P2, P3)**.
* Gera o arquivo final.

### 5. Resultado Final (Output)
Após a finalização (indicada pela barra de progresso 100%), o seu relatório estará pronto em:

`output/RELATORIO_PRIORIZACAO_FINAL.csv`

!!! success "Dica de Ouro"
    O arquivo gerado já está com os separadores e formatos ideais para o Excel brasileiro. Basta abrir e começar o direcionamento das equipes! 📊✅
