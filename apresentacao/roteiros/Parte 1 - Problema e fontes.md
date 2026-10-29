# Parte 1: Problema e fontes

Slides 1 a 6 · cerca de 5 minutos

A parte 1 responde “por que esse DW existe”: qual é o problema de política pública, qual é a pergunta e de onde vêm os dados. Se essa base ficar clara, o resto da apresentação se explica sozinho.

## Slide 1 · Capa

**O que o slide mostra.** O título do trabalho, a frase que resume o objetivo, três números do modelo (3 fatos, 9 dimensões, 5 consultas OLAP), os nomes do grupo e o mapa de São Carlos.

**A aula.** Um data warehouse (DW) é uma base de dados feita para análise, não para o dia a dia de um sistema. A definição clássica (Inmon) diz que ele é orientado a assunto, integrado, histórico e não volátil. No nosso caso, o assunto é a atenção primária à saúde (APS) em São Carlos. Integrado quer dizer que juntamos sistemas diferentes do SUS numa estrutura só. Histórico quer dizer que guardamos mês a mês, de 2023 a 2024. Não volátil quer dizer que os dados são carregados e consultados, não editados.

Os três números resumem o modelo multidimensional. Os **3 fatos** são os três processos que medimos: equipes, internações e produção ambulatorial. As **9 dimensões** são os ângulos pelos quais olhamos esses fatos (tempo, estabelecimento, diagnóstico etc.). As **5 consultas** são as perguntas que o DW responde, uma para cada operação OLAP pedida no enunciado.

**Como se liga ao trabalho.** O mapa não é decoração: o contorno é o limite oficial do município, da API de malhas do IBGE, e os pontos são as UBS e USF cadastradas no CNES. Já na capa aparecem duas das nossas fontes.

**Fala de exemplo**

> “Boa tarde, gente! O nosso trabalho é sobre a atenção primária à saúde aqui em São Carlos. A ideia foi montar um data warehouse que junta três coisas que normalmente ficam separadas: as equipes de saúde, os atendimentos e as internações que poderiam ter sido evitadas. No fim isso virou 3 tabelas de fatos, 9 dimensões e 5 consultas OLAP, que a gente vai mostrar. E esse mapa aí já é dado real: o contorno é do IBGE e os pontinhos são as unidades básicas cadastradas no CNES.”

## Slide 2 · Roteiro

**O que o slide mostra.** As quatro partes da apresentação e a barra de 20 minutos.

**A aula.** O roteiro segue a ordem natural de um projeto de DW. Primeiro se entende o problema e as fontes. Depois se modela cada processo de negócio como um esquema estrela. Em seguida as estrelas são unidas numa constelação, com os dados integrados. Por último o DW é usado: as consultas OLAP.

**Como se liga ao trabalho.** É a mesma estrutura que o enunciado pede para o relatório (descrição do problema, esquemas, consultas) e a mesma divisão de tempo igual por integrante.

**Fala de exemplo**

> “A apresentação tem quatro partes, uma pra cada um. A primeira é o problema e as fontes de dados. A segunda mostra os processos de negócio e as estrelas. A terceira junta tudo na constelação e explica como a gente integrou os dados. E a quarta fecha com as cinco consultas, já com os resultados reais.”

## Slide 3 · A porta de entrada do SUS

**O que o slide mostra.** Um fluxo: a UBS/USF acompanha o território; quando funciona, o paciente fica estável; quando falha, vira uma internação evitável (ICSAP). Embaixo, exemplos de condições e a portaria.

**A aula.** A atenção primária (ou atenção básica) é a porta de entrada do SUS. Ela acontece nas UBS (unidades básicas de saúde) e nas USF (unidades de saúde da família), onde trabalham as equipes de Saúde da Família (eSF): médico, enfermeiro, técnico e agentes comunitários. Cada equipe cuida de uma população de um território, de forma contínua.

Algumas doenças, quando bem acompanhadas, quase nunca precisam de hospital: hipertensão, diabetes, asma, pneumonia bacteriana, infecção urinária. Quando uma pessoa é internada por uma delas, é sinal de que o cuidado básico não chegou a tempo. Essas são as **internações por condições sensíveis à atenção primária (ICSAP)**. O Brasil tem uma lista oficial, na Portaria SAS/MS nº 221/2008, com 19 grupos de diagnósticos pela CID-10.

Por isso a taxa de ICSAP é o indicador clássico de efetividade da atenção básica: se ela cai, a APS está evitando internações. Um cuidado: o indicador também depende de renda, idade da população e acesso a hospital, então é um sinal, não uma prova.

**Como se liga ao trabalho.** No DW, a dimensão diagnóstico tem o atributo `icsap` (sim/não) e o `grupo_icsap`, que classificam cada código CID-10 segundo a portaria. Conferimos a lista com o texto oficial da portaria. É esse atributo que filtra as consultas 1, 3, 4 e 5.

**Fala de exemplo**

> “Pra entender o problema: a atenção básica é a porta de entrada do SUS, são as UBS e as unidades de Saúde da Família. Quando ela funciona, coisas como hipertensão, diabetes e asma são controladas ali no posto mesmo. Quando ela falha, a pessoa piora e acaba internada. Essas internações têm nome: ICSAP, internações por condições sensíveis à atenção primária. Tem uma lista oficial do Ministério, a Portaria 221 de 2008, com 19 grupos de doenças. E é por isso que ela é o indicador que a gente usa pra medir se a atenção básica tá funcionando.”

## Slide 4 · São Carlos no mapa

**O que o slide mostra.** O mapa do município, o zoom na área urbana e dois números: 254.857 habitantes e 36 UBS/USF no CNES.

**A aula.** Todo DW precisa de um recorte. O nosso é o município de São Carlos, código IBGE 3548906 (ou 354890 no padrão de 6 dígitos do DATASUS). A população do Censo 2022, conferida na API do IBGE, é 254.857. Ela é o denominador de duas medidas derivadas: a cobertura estimada de Saúde da Família e a taxa de ICSAP por 10 mil habitantes.

Os 36 estabelecimentos são os do tipo 02 (centro de saúde / unidade básica) na API de Dados Abertos do Ministério. Os pontos do mapa usam as coordenadas dessa API. Não há duplicatas (são 36 códigos CNES diferentes), mas várias unidades diferentes aparecem quase no mesmo lugar, a 5 a 25 metros uma da outra, e no mapa os pontos se sobrepõem. Há erros claros: a USF Água Vermelha, que fica no distrito, aparece dentro da cidade. A geolocalização da fonte é imprecisa.

**Como se liga ao trabalho.** Por causa disso, o DW não depende das coordenadas: a dimensão estabelecimento guarda o código CNES, o tipo de unidade e o bairro, e é por eles que se agrega. Isso também mostra uma atitude que vale a pena dizer em voz alta: olhar a qualidade da fonte antes de confiar nela.

**Fala de exemplo**

> “O nosso recorte é São Carlos: são 254.857 habitantes pelo Censo 2022, número que a gente conferiu direto na API do IBGE. Ele vai ser o denominador das taxas lá no final. E a cidade tem 36 unidades básicas cadastradas. Uma curiosidade: esses pontos no mapa vêm das coordenadas da API do Ministério, e várias são repetidas, dá pra ver o amontoado ali. Então a gente decidiu não depender delas: o DW agrega por código do estabelecimento e por bairro.”

## Slide 5 · A pergunta central

**O que o slide mostra.** A pergunta “Mais atenção básica significa menos internações evitáveis?” e três ângulos: oferta (equipes ativas), uso (atendimentos) e resultado (ICSAP).

**A aula.** Um DW é projetado a partir das perguntas que ele precisa responder, não a partir dos dados disponíveis. A nossa pergunta tem três peças, e cada uma vem de um sistema diferente do SUS. A **oferta** é quantas equipes de Saúde da Família existem (CNES). O **uso** é quanto essas unidades atendem (SIA). O **resultado** é quantas internações evitáveis acontecem (SIH).

Para comparar as três, elas precisam estar na mesma linha do tempo e no mesmo recorte geográfico. Isso exige dimensões em comum entre os três processos: é exatamente o que a constelação de fatos (parte 3) e a operação drill-across (consulta 5) permitem.

**Como se liga ao trabalho.** É a pergunta de política municipal que o tema do oferecimento pede: o resultado ajuda a decidir se vale expandir ou manter equipes. Todo o resto do modelo existe para responder a ela.

**Fala de exemplo**

> “E a pergunta que guia todo o trabalho é essa: mais atenção básica significa menos internações evitáveis? Pra responder, a gente precisa olhar três coisas juntas: a oferta, que é quantas equipes existem; o uso, que é quanto elas atendem; e o resultado, que são as ICSAP. O problema é que cada uma vem de um sistema diferente do SUS. Então o desafio do modelo é colocar as três na mesma linha do tempo, e isso a gente mostra mais pra frente.”

## Slide 6 · Cinco fontes, um data warehouse

**O que o slide mostra.** Três fontes principais (CNES, SIH-SUS, SIA-SUS), o caminho pelo PySUS com filtro de São Carlos e período 2023–2024, o DW em DuckDB e duas fontes auxiliares (IBGE e API do CNES).

**A aula.** As três fontes principais são do DATASUS:

- **CNES** (Cadastro Nacional de Estabelecimentos de Saúde): o arquivo EP traz as equipes e o ST traz os estabelecimentos.
- **SIH-SUS** (Sistema de Informações Hospitalares): o arquivo RD tem uma linha por AIH, a autorização de internação hospitalar.
- **SIA-SUS** (Sistema de Informações Ambulatoriais): o arquivo PA traz a produção ambulatorial, já parcialmente agregada.

As duas auxiliares completam o que falta: a API de localidades do IBGE dá nomes e regiões dos municípios, e a API de Dados Abertos do Ministério dá nome, bairro e coordenadas dos estabelecimentos.

O processo é um ETL (extração, transformação e carga). Os arquivos do DATASUS são estaduais e mensais, então baixamos cada mês de São Paulo com o PySUS, lemos em lotes e guardamos só as linhas de São Carlos. Foram 24 competências (jan/2023 a dez/2024), carregadas num banco DuckDB.

**Como se liga ao trabalho.** O enunciado pede pelo menos 2 fontes; usamos 5, todas públicas e oficiais. O notebook rodou com os dados reais: o DW ficou com 39.609 internações, 193.723 linhas de produção e 1.686 registros de equipe por mês. Para validar, comparamos com o TabNet do DATASUS: em janeiro de 2024, 1.287 AIHs de residentes lá contra 1.285 no DW, e a diferença são justamente as AIHs de continuação que descartamos de propósito.

**Fala de exemplo**

> “De onde vem tudo isso? Cinco fontes públicas. As três principais são do DATASUS: o CNES, que tem as equipes e os estabelecimentos; o SIH, com uma linha por internação; e o SIA, com a produção ambulatorial. E duas de apoio: o IBGE pros nomes dos municípios e a API do Ministério pra nome e bairro das unidades. A gente baixou com o PySUS. Os arquivos são do estado inteiro, mês a mês, então a gente filtrou São Carlos e juntou 2023 e 2024 num banco DuckDB. E a gente conferiu com o TabNet do Ministério: os números batem. Agora vamos ver como isso virou modelo.”

## Lembretes

- As explicações são para estudar antes: leiam a parte de vocês e também a dos outros, porque a professora pode perguntar qualquer coisa a qualquer um.
- As falas têm de 40 segundos a 1 minuto por slide. Não decorem palavra por palavra: guardem a ideia e os números.
- Os números citados são os resultados reais do notebook (dados de 2023 e 2024). As mesmas falas, em versão curta, estão nas notas do apresentador (tecla N na apresentação).
