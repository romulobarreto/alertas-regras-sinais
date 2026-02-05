# 📋 Matriz de Priorização de Inspeções

Nossa inteligência separa o "joio do trigo". Abaixo, a lógica técnica que o Python executa para gerar o relatório final.

| Prioridade | Nome do Alerta / Regra | Lógica Técnica (O que o Python faz) |
| :--- | :--- | :--- |
| **P1** 🚨 | **Desligado com Reclamação** | Status `DS` + Nota de Reclamação (após o desligamento da UC) + Sem fiscalização/Bate-Caixa (após o desligamento da UC). |
| **P1** 🚨 | **Mínimo da Fase com Reclamação** | Status `LG` + Consumo no mínimo da fase (4 meses) + Nota de Reclamação + Sem fiscalização/Bate-Caixa recente (4 meses). |
| **P2** ⚠️ | **Reincidente com Queda** | Status `LG` + Histórico de deficiência técnica + Queda de média anual (YoY) ≥ 40% + Sem fiscalização/Bate-Caixa recente (6 meses). |
| **P2** ⚠️ | **Mínimo com Apontamento** | Status `LG` + Consumo no mínimo da fase + Leiturista anotou vestígio/defeito + Sem fiscalização/Bate-Caixa recente (4 meses). |
| **P2** ⚠️ | **Dowertech 2014 no Mínimo** | Fabricante `DOWERTECH` + Ano `2014` + Status `LG` + Consumo no mínimo da fase + Sem fiscalização/Bate-Caixa (4 meses). |
| **P3** 🔍 | **Medidor Antigo no Mínimo** | Ano do Medidor <= 2000 + Status `LG` + Consumo no mínimo da fase + Sem fiscalização/Bate-Caixa recente (4 meses). |
| **P3** 🔍 | **Condomínio Alto DS** | Endereço marcado como `CONDOMINIO` que possui 5 ou mais UCs com status `DS` simultaneamente. |
| **P3** 🔍 | **Desligado Recente + Deficiência Técnica** | Status `DS` nos últimos 6 meses + Já teve deficiência técnica em algum momento + Sem fiscalização/Bate-Caixa recente após o desligamento da UC. |
| **P3** 🔍 | **Consumo no Mínimo** | Status `LG` + Consumo no mínimo da fase + Sem fiscalização/Bate-Caixa recente (4 meses). |
| **P3** 🔍 | **Queda Acentuada** | Status `LG` + Queda de média anual (YoY) ≥ 40% + Sem fiscalização/Bate-Caixa recente (6 meses). |

!!! info "O que é o Bate-Caixa nas regras?"
    O **Bate-Caixa** agora é tratado com o mesmo peso de uma **Fiscalização**. Se a equipe passou na frente da casa e não encontrou nada, o sistema entende que aquele alvo não deve ser visitado novamente por um período de 4 a 6 meses, poupando tempo e combustível. ⛽💰