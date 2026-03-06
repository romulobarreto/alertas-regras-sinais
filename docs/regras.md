# 📋 Matriz de Priorização de Inspeções

Nossa inteligência separa o "joio do trigo". Abaixo, a lógica técnica que o Python executa para gerar o relatório final.

| Prioridade | Alerta / Regra / Sinal| Lógica Técnica |
| :--- | :--- | :--- |
| **P1** 🚨 | Prospecção dos motoqueiros | Visita do prospector + Irregularidade confirmada + **sem** visita posterior |
| **P1** 🚨 | Desligado com Reclamação | `DS` + nota de reclamação (após desligamento da UC)+ **sem** visita após desligamento da UC |
| **P1** 🚨 | Mínimo da Fase com Reclamação | `LG` + mínimo (4m) + nota de reclamação + **sem** visita (4m) |
| **P2** ⚠️ | Prospecção dos motoqueiros | Visita do prospector + Indício de irregularidade + **sem** visita posterior |
| **P2** ⚠️ | Reincidente com Queda | `LG` + histórico de irregularidade + queda de consumo maior que 40% + **sem** visita (6m) |
| **P2** ⚠️ | Mínimo com Apontamento Suspeito | `LG` + mínimo + apontamento relevante do leiturista + **sem** visita (4m) |
| **P2** ⚠️ | Dowertech 2013 - 2015 no Mínimo | fabricante `DOWERTECH` + ano 2013 - 2015 + `LG` + mínimo + **sem** visita (4m) |
| **P3** 🔎 | Medidor Antigo no Mínimo | ano <= 2000 + `LG` + mínimo + **sem** visita (4m) |
| **P3** 🔎 | Desligado Recente + Irregularidade | `DS` (6m) + histórico de irregularidade + **sem** visita após desligamento da UC |
| **P3** 🔎 | Consumo no Mínimo | `LG` + mínimo (4m) + **sem** visita (4m) |
| **P3** 🔎 | Queda Acentuada | `LG` + queda de consumo maior que 40% + cliente convencional + **sem** visita (6m) |
| **P3** 🔎 | Condomínio com Alto DS | condomínio com **>= 5 UCs** em `DS` + **sem** visita (6m) |

`Sistema desconsidera alvos já abertos por outras áreas.`

**Alvos que já estão abertos por outras áreas** são removidos do conjunto de priorização, evitando retrabalho e duplicidade de atuação.

!!! info "O que é o **sem visita** nas regras?"
    O **sem visita** nada mais é do que o **Bate-Caixa, Faro-Certo e Inspeção**, todos tratados com **o mesmo peso**. Se a equipe passou na frente da casa e solicitou consumo mas não encontrou nada, o sistema entende que aquele alvo não deve ser visitado novamente por um período de 4 a 6 meses, poupando tempo e combustível. ⛽💰

!!! info "O que é o **apontamento suspeito** nas regras?"
    O **apontamento suspeito** nada mais é do que o apontamento realizado pelo leiturista no momento da visita na UC, nem sempre a leitura é coletada normalmente (**LEITURA NORMAL**). 
    
    📝 **Os apontamentos suspeitos são:**
    'VESTIGIO DE IRREGULARIDADE',
    'VESTIGIO DE LIGACAO IRREGULAR',
    'PROB DISPLAY MEDIDOR ELETRONICO',
    'MEDIDOR COM VIDRO QUEBRADO',
    'MEDIDOR PARADO DESCONTROLADO OU EMBACADO',
    'MEDIDOR GIRANDO AO CONTRARIO',
    'MEDIDOR NAO LOCALIZADO',
    'MEDIDOR RETIRADO DA CAIXA DE MEDICAO',
    'NUMERO DO MEDIDOR NAO CONFERE',
    'MEDIDOR COM VIDRO EMBACADO (NAO PERMITE LEITURA)',
    'MEDIDOR DESENERGIZADO (NAO EXIBE LEITURA)',
    'IMPEDIMENTO DE LEITURA POR SINISTRO',
    'EQUIPAMENTO COM PERDA DE PARAMETRO',
    'ERRO DE CADASTRO',
    'TROCA DE EQUIPAMENTO POR ENCHENTE'.