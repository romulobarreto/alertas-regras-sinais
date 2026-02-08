# 📋 Matriz de Priorização de Inspeções

Nossa inteligência separa o "joio do trigo". Abaixo, a lógica técnica que o Python executa para gerar o relatório final.

| Prioridade | Alerta / Regra / Sinal| Lógica Técnica |
| :--- | :--- | :--- |
| **P1** 🚨 | Desligado com Reclamação | `DS` + tem reclamação (após move-out)+ **sem** visita após move-out |
| **P1** 🚨 | Mínimo da Fase com Reclamação | `LG` + mínimo (4m) + reclamação + **sem** visita (4m) |
| **P1** 🚨 | Prospecção dos motoqueiros | Visita do prospector + Irregularidade confirmada + **sem** visita posterior |
| **P2** ⚠️ | Prospecção dos motoqueiros | Visita do prospector + Indício de irregularidade + **sem** visita posterior |
| **P2** ⚠️ | Reincidente com Queda | `LG` + fraude histórica + YoY ≤ -40% + **sem** visita (6m) |
| **P2** ⚠️ | Mínimo com Apontamento Suspeito | `LG` + mínimo + apontamento relevante + **sem** visita (4m) |
| **P2** ⚠️ | Dowertech 2013, 2014 no Mínimo | fabricante `DOWERTECH` + ano 2014 + `LG` + mínimo + **sem** visita (4m) |
| **P3** 🔎 | Medidor Antigo no Mínimo | ano <= 2000 + `LG` + mínimo + **sem** visita (4m) |
| **P3** 🔎 | Desligado Recente + Fraude | `DS` (6m) + fraude histórica + **sem** visita após move-out |
| **P3** 🔎 | Consumo no Mínimo | `LG` + mínimo (4m) + **sem** visita (4m) |
| **P3** 🔎 | Queda Acentuada | `LG` + YoY ≤ -40% + **sem** visita (6m) |
| **P3** 🔎 | Condomínio com Alto DS | condomínio com **>= 5 UCs** em `DS` no mesmo endereço |

!!! info "O que é o Bate-Caixa e Faro-Certo nas regras?"
    O **Bate-Caixa e Faro-Certo** agora é tratado com o mesmo peso de uma **Fiscalização**. Se a equipe passou na frente da casa e não encontrou nada, o sistema entende que aquele alvo não deve ser visitado novamente por um período de 4 a 6 meses, poupando tempo e combustível. ⛽💰