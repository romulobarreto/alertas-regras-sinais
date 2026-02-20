### 🧾 Atualizações recentes 
Saiba tudo sobre as atualizações do projeto por período.

### ✅ Ajuste 16 (20/02/26) — Regra do P2 de medidor dowertech 2015 no mínimo da fase
Para um P2 mais **assertivo** adicionamos a regra do **medidor dowertech 2015 no mínimo da fase** para  **sinal P2**.

### ✅ Ajuste 15 (20/02/26) — Ajusta as regras de negócio do P3 de condomínios
Sinais para dias de **chuva** não estavam sendo assertivos por **erro de lógica**. Script alterado para verificar **condomínimos sem visitas no últimos 6 meses**, dessa forma, **encontrando condomínios com alto índice de DS que ainda não foram visitados**.

### ✅ Ajuste 14 (12/02/26) — Ajusta as regras de negócio do P3 de condomínios
Sinais para dias de **chuva** não estavam funcionando por **erro de lógica**. Script alterado para verificar **endereço e número do imóvel de forma individual**, dessa forma, conseguindo encontrar endereços iguais e **encontrando condomínios com alto índice de DS**.

### ✅ Ajuste 13 (07/02/26) — Ajusta as regras de negócio do P3
Para que os **sinais** possam ser mais **assertivos** alterados a regra de nogócio do **P3-Queda acentuada de consumo** para que **desconsidere** os clientes **micro-geradores**.

### ✅ Ajuste 12 (07/02/26) — Ajusta o painel de priorização para aceitar filtro pelo mapa
Para que as UCs possam ser **filtradas** pelo mapa, foi adicionado novas funções ao mapa.

### ✅ Ajuste 11 (07/02/26) — Adição das prospecções realizadas pelos motoqueiros
Para que o resultado dos **alertas-regras-sinais** sejam mais **assertivos**, consideramos as **prospecções dos motoqueiros**.

### ✅ Ajuste 10 (07/02/26) — Adição do faro certo para a contabilização de visitas
Para que o resultado dos **alertas-regras-sinais** sejam mais **assertivos**, consideramos as consultas realizadas pelo **faro_certo** como visitas nas UCs.

### ✅ Ajuste 9 (06/02/26) — Ajuste de colunas no relatório final
Para que no painel de prioridades os filtro sejam **mais rápidos** removemos as colunas de **consumo e year over year**, tornando a base mais **leve**.

### ✅ Ajuste 8 (06/02/26) — Ajuste de nome dos Motivo Prioridade
Para que no painel de prioridades o filtro **Motivo Prioridade** contenha o tipo de prioridade o nome de cada motivo recebeu **P1 - P2 - P3** no prefixo.

### ✅ Ajuste 7 (06/02/26) — Ajuste de filtro do Motivo Prioridade
No painel de prioridades o filtro **Motivo Prioridade** não estava aceitando **nenhum filtro**.

### ✅ Ajuste 6 (05/02/26) — Regra do P2 de medidor dowertech 2014 no mínimo da fase
Para um P2 mais **assertivo** adicionamos a regra do **medidor dowertech 2014 no mínimo da fase** para  **sinal P2**.

### ✅ Ajuste 5 (05/02/26) — Regra do P2 de medidor antigo no mínimo da fase
Para um P2 mais **assertivo** passamos o P2 de **medidor antigo no mínimo da fase** para  **sinal P3**.

### ✅ Ajuste 4 (04/02/26) — Ajuste do link do painel de priorização
Para um **link** mais **profissional** a url do site foi alterada. 

### ✅ Ajuste 3 (02/02/26) — Deploy do streamlit para visualização dos dados
Para **melhor visualização** dos alvos encontrados, foi feito o **painel de prioridades** com streamlit.

🌐 Acesse: 
[Painel de Priorização (Streamlit)](https://painel-priorizacao.streamlit.app/) 

### ✅ Ajuste 2 (02/02/26) — Regra do P1 DS com corte por MOVE_OUT
Para o alvo **P1 DS**, a **nota de reclamação** só é considerada quando ocorrer em data **maior ou igual** ao período de **MOVE_OUT**.  
Isso evita “puxar” reclamações antigas que não representam o contexto atual após a troca/mudança.

### ✅ Ajuste 1 (02/02/26) — Desconsiderar alvos já abertos
Agora, **alvos que já estão abertos por outras áreas** são removidos do conjunto de priorização, evitando retrabalho e duplicidade de atuação.

### ✅ Deploy (31/01/26) — Deploy do ETL sem visualização
**De +-5horas para 40 segundos.** ETL completo da geração de alertas, regras e sinais da regional sul.