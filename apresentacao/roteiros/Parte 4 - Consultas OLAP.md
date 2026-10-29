# Parte 4: Consultas OLAP

Slides 18 a 24 · cerca de 5 minutos

A parte 4 é o DW funcionando: cinco consultas, uma para cada operação OLAP, todas com os dados reais de 2023 e 2024. São 8 slides em 5 minutos, então o ritmo é: nome da operação, o que ela faz, o achado principal, próximo slide.

## Slide 18 · Abertura: cinco consultas OLAP

**O que o slide mostra.** O divisor da parte 4 e as cinco operações.

**A aula.** OLAP (On-Line Analytical Processing) é a análise interativa dos dados como um cubo multidimensional. As cinco operações pedidas no enunciado são:

- **Roll-up**: sobe numa hierarquia e agrega (mês → ano).
- **Drill-down**: desce numa hierarquia e detalha (grupo → procedimento).
- **Slice and dice**: o slice fixa um valor de uma dimensão (ano = 2024); o dice recorta um subcubo restringindo várias dimensões.
- **Pivot**: gira os eixos da tabela, sem mudar os dados.
- **Drill-across**: combina medidas de fatos diferentes através das dimensões conformes.

**Como se liga ao trabalho.** Cada consulta usa uma operação e responde uma pergunta de gestão. A última é a pergunta central.

**Fala de exemplo**

> “Agora a parte boa: o DW funcionando. São cinco consultas, uma pra cada operação OLAP: roll-up, drill-down, slice and dice, pivot e drill-across. E tudo que eu vou mostrar é dado real de 2023 e 2024.”

## Slide 19 · Consulta 1: roll-up

**O que o slide mostra.** As ICSAP de residentes em três níveis de tempo: 24 barras mensais, 8 trimestrais e 2 anuais.

**A aula.** O roll-up sobe na hierarquia do tempo (`ano_mes ≤ trimestre ≤ ano`) e soma as internações em cada nível. Funciona porque `qtd_internacoes` é aditiva. No SQL do notebook foi usado o `GROUP BY ROLLUP (ano, trimestre)`, que devolve de uma vez os trimestres, os subtotais de cada ano e o total geral. Elementos do esquema: `fato_internacao`, com filtro ICSAP = sim e residência = São Carlos.

**Os resultados.**

- Foram **5.255** ICSAP de residentes em dois anos, **16%** das 32.799 internações de residentes.
- No mês, o maior valor é dezembro de 2023 (**291**) e o menor é janeiro de 2024 (**167**). O mês é o de processamento da AIH, então parte desse sobe e desce é o ritmo de apresentação dos hospitais.
- No trimestre a série fica estável, entre **572 e 728**.
- No ano: **2.700** em 2023 e **2.555** em 2024, queda de cerca de **5%**.

**Como se liga ao trabalho.** É o indicador de resultado da pergunta central, visto em várias escalas. A lição do roll-up aparece nos dados: a visão mensal é ruidosa, a anual mostra a tendência.

**Fala de exemplo**

> “A primeira é um roll-up no tempo. A gente pega as internações evitáveis de quem mora em São Carlos mês a mês e vai subindo: trimestre, depois ano. Foram 5.255 em dois anos, 16% de todas as internações de moradores. No mês oscila bastante, de 167 a 291, até porque o mês aqui é o de processamento da AIH. Mas quando sobe pra trimestre fica bem estável, e no ano dá pra ver uma queda de uns 5%, de 2.700 pra 2.555.”

## Slide 20 · Consulta 2: drill-down

**O que o slide mostra.** Três colunas de barras: os grupos do SIGTAP, os subgrupos do grupo 02 e os procedimentos do subgrupo 0202. A barra destacada é o caminho escolhido em cada nível.

**A aula.** O drill-down faz o caminho inverso do roll-up: parte de um total agregado e desce na hierarquia do procedimento (`procedimento ≤ subgrupo ≤ grupo`), sempre abrindo o item de maior volume. Elementos do esquema: `fato_producao_ambulatorial`, filtrado pelo município do estabelecimento (uma consulta de oferta: o que a rede de São Carlos produz). Medidas: soma de `qtd_aprovada` e `valor_aprovado`.

**Os resultados.**

- O grupo **02 (finalidade diagnóstica)** lidera em quantidade, com **1,77 milhão** de procedimentos aprovados.
- O grupo **03 (procedimentos clínicos)** vem em segundo em quantidade (1,06 milhão), mas tem o **maior valor aprovado: cerca de R$ 31,3 milhões**, contra R$ 18 milhões do grupo 02.
- No grupo 02, o subgrupo **0202 (laboratório clínico)** concentra **1,39 milhão**.
- No procedimento: **hemograma completo** (126.646) e **dosagem de creatinina** (101.989). Os nomes vêm da tabela SIGTAP.

**Como se liga ao trabalho.** Mostra o que a rede ambulatorial mais faz e onde está o gasto, o que apoia o dimensionamento de oferta e de contratos. Vale reparar na diferença entre volume e valor: exame de laboratório é muito e barato, procedimento clínico é menos e caro.

**Fala de exemplo**

> “A segunda é um drill-down, o contrário: começa no geral e vai descendo. Aqui é a produção ambulatorial dos estabelecimentos de São Carlos. No nível de grupo, o que mais tem é procedimento diagnóstico, 1,8 milhão. Só que em dinheiro quem ganha é o grupo de procedimentos clínicos, uns 31 milhões de reais. Aí a gente desce no diagnóstico: o subgrupo é laboratório clínico, e no procedimento aparecem hemograma e creatinina, que são aqueles exames de rotina que todo mundo já fez.”

## Slide 21 · Consulta 3: slice and dice

**O que o slide mostra.** À esquerda, um cubo com a fatia escolhida em destaque; à direita, as ICSAP de idosos em 2024 por causa e sexo, com a média de dias.

**A aula.** Imagine os dados como um cubo com três eixos: tempo, ciclo de vida e diagnóstico. O **slice** corta uma fatia fixando um valor de uma dimensão: ano = 2024. O **dice** recorta um subcubo restringindo outras dimensões: ciclo de vida = idoso e diagnóstico ICSAP = sim. O que sobra é analisado por causa e sexo. A média de dias é a medida derivada: soma dos dias dividida pelo número de internações.

**Os resultados.**

- Foram **1.358** internações evitáveis de idosos residentes em 2024.
- **Doenças cerebrovasculares** lideram: **170 homens e 154 mulheres**.
- Depois vem a **insuficiência cardíaca**: **128 mulheres e 114 homens**.
- As internações mais longas são de **doenças pulmonares (9,5 dias)** e **insuficiência cardíaca (8 dias)**.

**Como se liga ao trabalho.** São condições crônicas que a atenção básica acompanha (pressão, coração). Para o gestor, isso aponta onde ações para idosos, como grupos de hipertensos e visitas domiciliares, poderiam evitar internações.

**Fala de exemplo**

> “A terceira é o slice and dice. Pensa no cubo: o slice corta uma fatia, só o ano de 2024. O dice recorta um pedaço dessa fatia: só idosos e só internações evitáveis. Deu 1.358 internações. O que mais interna idoso são as doenças cerebrovasculares, tipo AVC, 170 homens e 154 mulheres, e depois insuficiência cardíaca. E a última coluna é a média de dias: doença pulmonar fica 9 dias e meio internada. São justamente coisas que a atenção básica devia segurar.”

## Slide 22 · Consulta 4: pivot

**O que o slide mostra.** Dois mapas de calor com os mesmos números: à esquerda, causas nas linhas e ciclo de vida nas colunas; à direita, a mesma tabela girada. Quanto mais escura a célula, maior o valor.

**A aula.** O pivot (ou rotação) troca linhas e colunas. Os dados não mudam, só a leitura. Elementos do esquema: `fato_internacao` cruzando diagnóstico (grupo ICSAP) e perfil do paciente (ciclo de vida), residentes, 2023 e 2024. O slide mostra as 7 causas mais frequentes.

**Os resultados.**

- Leitura por causa (linhas): as doenças circulatórias são quase só de adultos e idosos. São **621 idosos** com doença cerebrovascular e **557** com insuficiência cardíaca.
- Leitura por fase da vida (girada): nas **crianças** dominam as **doenças pulmonares (329), seguidas da asma (159), que fica fora das 7 causas mostradas no slide**. Nos **adultos**, as maiores são doenças cerebrovasculares (229), infecção do rim e trato urinário (204) e infecção de pele (189).

**Como se liga ao trabalho.** As duas leituras servem a decisões diferentes: “quais causas pesam em cada fase da vida” orienta programas por público (saúde da criança, do idoso); “qual fase sofre mais com cada causa” orienta linhas de cuidado por doença.

**Fala de exemplo**

> “A quarta é o pivot. É a mesma tabela, só que girada, e cada jeito responde uma pergunta diferente. Olhando por causa, dá pra ver que doença circulatória é coisa de adulto e idoso: 621 idosos com doença cerebrovascular. Girando e olhando por fase da vida, aparece outra coisa: nas crianças o que domina é doença pulmonar, 329. Então o mesmo dado serve tanto pra um programa de saúde do idoso quanto pra uma linha de cuidado pra asma infantil, por exemplo.”

## Slide 23 · Consulta 5: drill-across

**O que o slide mostra.** Dois painéis empilhados, com o mesmo eixo de meses: a cobertura estimada (`fato_equipe`), em duas linhas, só eSF e eSF + eAP, e a ICSAP por 10 mil habitantes (`fato_internacao`). Uma nota embaixo lembra que a produção das UBS não está no SIA.

**A aula.** O drill-across combina medidas de **fatos diferentes**. A regra é não juntar os fatos linha a linha, porque eles têm grãos diferentes e a junção multiplicaria linhas. Em vez disso, cada fato é agregado sozinho até o grão comum (o mês) e só então os resultados são juntados pela dimensão conforme `ano_mes`. Isso só é possível por causa da constelação.

- **Oferta** (`fato_equipe`): contagem de equipes por mês. Cobertura estimada = equipes × 3.450 ÷ 254.857, sendo 3.450 o parâmetro clássico de pessoas por equipe de Saúde da Família. A linha de baixo conta só as eSF (as 23 USF). A de cima soma as eAP das UBS tradicionais como se cada uma fosse uma equipe inteira; como a eAP é menor, essa linha é um **teto**. A cobertura real da atenção básica fica entre as duas.
- **Uso** (`fato_producao_ambulatorial`): a consulta do relatório também soma a produção aprovada nos estabelecimentos de atenção primária, mas o resultado é zero (veja abaixo), por isso esse painel saiu do slide.
- **Resultado** (`fato_internacao`): ICSAP de residentes. Taxa = ICSAP ÷ 254.857 × 10.000.

**Os resultados.**

- **23 equipes** de Saúde da Família em todos os 24 meses, ou seja, cobertura estimada constante de **31,1%**.
- Com as **11 a 13 eAP**, o teto oscila entre **46% e 48,7%** e termina em 46,0%. É uma variação pequena, de uma ou duas equipes.
- A produção das UBS no SIA é **zero em todos os meses**: desde o e-SUS APS, ela é registrada no **SISAB**, outro sistema. Por isso o slide mostra só oferta e internações, e a nota embaixo explica.
- A taxa de ICSAP variou entre **6,55 e 11,42 por 10 mil habitantes** e terminou 2024 em **8,40**.

**Como se liga ao trabalho.** É a resposta (honesta) à pergunta central. O DW consegue fazer a comparação, mas os dados de 2023–2024 não permitem concluir nada: a oferta não variou, então não há o que relacionar com as internações. Esse é um achado real do trabalho, e vale apresentar como achado, não como falha.

**Fala de exemplo**

> “E a quinta é a pergunta central, o drill-across. Aqui a gente pega fatos diferentes, agrega cada um sozinho por mês e junta pelo mês, que é a dimensão conforme. E vieram duas surpresas. Primeiro: São Carlos teve 23 equipes de Saúde da Família todo santo mês, então a cobertura de Saúde da Família ficou parada em 31%. Se a gente somar as UBS tradicionais, contando cada uma como equipe inteira, o máximo chega a uns 46 a 49%; a cobertura real fica entre as duas linhas. Segundo: a produção das UBS no SIA é zero, porque desde o e-SUS ela vai pra outro sistema, o SISAB. Por isso o gráfico mostra só a oferta e as internações. As internações evitáveis ficaram entre 6,5 e 11,4 por 10 mil habitantes. Então o DW faz a pergunta, mas com a oferta parada ainda não dá pra responder.”

## Slide 24 · Obrigado

**O que o slide mostra.** O encerramento e o convite para perguntas.

**A aula.** O fechamento retoma a frase do início: três processos, uma constelação e uma pergunta de política pública para São Carlos.

**Como se liga ao trabalho.** Na hora das perguntas, cada um responde sobre a própria parte, mas todos devem saber explicar a pergunta central, a constelação e o achado do SISAB.

**Limites, para as perguntas.** Não há mais um slide só para eles, mas a banca pode perguntar. Dizê-los com clareza mostra que o grupo entendeu os dados:

- **SISAB ≠ SIA**: a produção das UBS não está no SIA. Os dados reais confirmaram: zero em 2023 e 2024.
- **Cobertura estimada**: usa o parâmetro de 3.450 pessoas por equipe e conta só equipes de Saúde da Família. A metodologia oficial de cobertura mudou ao longo dos anos.
- **Competência**: o mês do DW é o de processamento, não a data da internação. Uma internação de dezembro pode aparecer em janeiro.
- **Coordenadas**: as da API do CNES são imprecisas.

O próximo passo sai direto daí: incluir o SISAB como fonte e usar mais anos, para que a oferta tenha variação.

**Fala de exemplo**

> “Então é isso: três processos, uma constelação e uma pergunta de política pública pra São Carlos, já rodando com dado real. Obrigado, e a gente fica aberto pra perguntas!”

## Lembretes

- As explicações são para estudar antes: leiam a parte de vocês e também a dos outros, porque a professora pode perguntar qualquer coisa a qualquer um.
- As falas têm de 40 segundos a 1 minuto por slide. Não decorem palavra por palavra: guardem a ideia e os números.
- Os números citados são os resultados reais do notebook (dados de 2023 e 2024). As mesmas falas, em versão curta, estão nas notas do apresentador (tecla N na apresentação).
