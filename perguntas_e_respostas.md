# Perguntas de banca: DW da Atenção Básica em São Carlos

Simulação de arguição da professora sobre o Trabalho Prático 1 (SCC0245). As perguntas vão da mais básica à mais avançada; no fim há uma seção com as críticas mais prováveis ao modelo e como responder a cada uma.
Os números citados vêm do relatório e do notebook (dados reais de jan/2023 a dez/2024).

---

## Nível 1: o problema e as fontes

**1. Qual é o tema do trabalho, em uma frase?**
A cobertura da atenção básica em São Carlos, vista por três ângulos: a oferta de equipes de saúde, a produção ambulatorial e as internações que poderiam ter sido evitadas com uma atenção primária efetiva (ICSAP).

**2. Por que esse tema interessa à gestão municipal?**
A atenção básica é responsabilidade direta do município: é ele quem abre UBS/USF e contrata equipes. O DW ajuda a responder perguntas como "quantas equipes temos e onde estão?", "quais internações da nossa população seriam evitáveis, em quem e por quê?" e "quando a oferta muda, as internações evitáveis mudam junto?". Com as respostas, o gestor pode decidir onde reforçar equipes e quais linhas de cuidado priorizar.

**3. O que é ICSAP?**
Internação por Condição Sensível à Atenção Primária: uma internação por uma doença que, bem acompanhada no posto de saúde, normalmente não chegaria ao hospital (hipertensão, diabetes, asma, infecção urinária, insuficiência cardíaca etc.). A lista oficial brasileira está na Portaria SAS/MS nº 221/2008, com 19 grupos de causas definidos por códigos CID-10. A taxa de ICSAP é um dos indicadores mais usados para avaliar a efetividade da atenção básica.

**4. Quais fontes de dados vocês usaram?**
Três principais, todas do DATASUS e baixadas com o PySUS:
- **CNES** (arquivos EP, de equipes, e ST, de estabelecimentos);
- **SIH-SUS**, arquivo RD (uma linha por AIH, ou seja, por internação);
- **SIA-SUS**, arquivo PA (produção ambulatorial).

E duas auxiliares: a **API de Localidades do IBGE** (nomes e regiões dos municípios) e a **API de Dados Abertos do Ministério da Saúde** (nome, bairro e coordenadas dos estabelecimentos). São cinco fontes no total; o enunciado pede no mínimo duas.

**5. Os dados são reais?**
Sim, todos são públicos e oficiais. O notebook rodou com os 24 meses de 2023 e 2024 e o DW final tem 1.686 linhas em `fato_equipe`, 39.609 em `fato_internacao` e 193.723 em `fato_producao_ambulatorial`. Não usamos dados sintéticos.

**6. Qual é o recorte temporal e geográfico?**
De janeiro de 2023 a dezembro de 2024. Os arquivos do DATASUS são estaduais (SP) e mensais, e o ETL mantém só o que se liga a São Carlos (código IBGE 354890): equipes sediadas no município e internações ou atendimentos de pacientes **residentes** em São Carlos **ou atendidos** em São Carlos.

**7. Por que guardar os dois critérios, residência e local de atendimento?**
Porque eles respondem perguntas diferentes. A demanda da população (ICSAP de moradores) deve ser filtrada por residência, já que um morador de São Carlos pode ser internado em Araraquara. A oferta da rede instalada (o que os hospitais e ambulatórios da cidade fazem) é filtrada pelo município do estabelecimento, que também atende moradores da região.

**8. Que população vocês usaram nas taxas?**
A do Censo 2022 do IBGE: 254.857 habitantes, conferida na API do IBGE (agregado 9514).

---

## Nível 2: conceitos de modelagem dimensional

**9. Quais são os processos de negócio?**
1. Oferta de equipes da atenção básica → `fato_equipe`.
2. Internações hospitalares → `fato_internacao`.
3. Produção ambulatorial → `fato_producao_ambulatorial`.

**10. O que é o grão de uma tabela de fatos? Qual é o grão de cada uma?**
O grão diz o que uma linha da tabela de fatos representa e deve ser definido antes das dimensões e das medidas.
- `fato_equipe`: uma equipe ativa em um estabelecimento em um mês.
- `fato_internacao`: uma internação (uma AIH).
- `fato_producao_ambulatorial`: estabelecimento × procedimento × mês × perfil do paciente × município de residência × CBO. É o menor detalhe que o arquivo público do SIA oferece, porque ele já vem parcialmente agregado.

**11. Qual a diferença entre medida aditiva, semiaditiva e não aditiva? Dê um exemplo de cada no trabalho.**
- **Aditiva:** pode ser somada em qualquer dimensão. Exemplo: `valor_total` da internação, que soma por mês, hospital, causa etc.
- **Semiaditiva:** soma em algumas dimensões, mas não em outras. Exemplo: o número de equipes, que soma entre estabelecimentos e tipos de equipe mas não ao longo do tempo (a mesma equipe aparece em janeiro e em fevereiro).
- **Não aditiva:** não pode ser somada. Exemplo: a taxa de aprovação do SIA (aprovado ÷ apresentado), a cobertura estimada e a taxa de ICSAP por 10 mil habitantes.

**12. Se não pode somar o número de equipes no tempo, como agregar de mês para ano?**
Usando a média das contagens mensais ou o valor do último mês do período (fotografia de fim de período). Somar 12 meses de 23 equipes daria 276 "equipes", o que não faz sentido.

**13. O que é uma tabela de fatos sem fato? Por que a `fato_equipe` é assim?**
É uma tabela de fatos sem medida numérica: cada linha só registra que um evento ou uma situação existiu. A `fato_equipe` registra que uma equipe estava ativa em um estabelecimento num mês. Não há nada para medir além da existência, e a análise é feita contando linhas (`COUNT`).

**14. Por que a `fato_equipe` é um snapshot periódico e não uma tabela de transações?**
Porque o CNES publica uma fotografia mensal do cadastro (competência), não eventos de "equipe criada" e "equipe desativada". O modelo segue o que a fonte entrega: uma foto por mês.

**15. O que é dimensão degenerada? Onde aparece?**
É um identificador que fica na própria tabela de fatos, sem tabela de dimensão, porque não tem outros atributos. No trabalho: `n_aih` em `fato_internacao` e `id_equipe` em `fato_equipe`. Eles servem para contar itens distintos (por exemplo, `COUNT(DISTINCT id_equipe)`) e para rastrear o registro de volta à fonte.

**16. O que é a tabela bugiganga (junk dimension)? Por que vocês criaram uma?**
É uma dimensão que reúne indicadores de baixa cardinalidade que, sozinhos, virariam dimensões minúsculas. A `dim_junk_internacao` junta caráter do atendimento (eletivo, urgência, acidentes), óbito (sim/não) e uso de UTI (sim/não). Ela contém só as combinações que ocorrem nos dados, e assim a tabela de fatos tem uma chave estrangeira em vez de três.

**17. Por que usar chaves artificiais (`sk_*`) em vez dos códigos das fontes?**
- Isolam o DW das mudanças de código nas fontes.
- Permitem o membro 0, "Não informado".
- Uniformizam códigos que vêm em formatos diferentes (CNES com ou sem zeros à esquerda, município com 6 ou 7 dígitos).
- São inteiros pequenos, o que deixa a tabela de fatos menor e as junções mais rápidas.
- Se um dia for preciso guardar histórico de uma dimensão (SCD tipo 2), a chave natural sozinha não daria conta.

**18. Para que serve o membro "Não informado" (chave 0)?**
Para que nenhum fato seja perdido na carga quando um código não é encontrado na dimensão (CID inválido, CBO em branco etc.). O fato aponta para a linha 0 em vez de ficar com a chave nula ou ser descartado. Por isso "todas as chaves resolvidas" é um critério de validação da carga.

**19. O que é hierarquia de dimensão? Dê exemplos.**
É uma sequência de níveis do mais detalhado ao mais agregado, em que cada valor de um nível pertence a um único valor do nível acima. Notação: `A ≤ B`.
- `ano_mes ≤ trimestre ≤ semestre ≤ ano`
- `cod_procedimento ≤ forma_organizacao ≤ subgrupo ≤ grupo` (o próprio código SIGTAP é hierárquico: prefixos de 6, 4 e 2 dígitos)
- `cid ≤ cid_categoria ≤ capitulo` e `cid ≤ grupo_icsap ≤ icsap`
- `faixa_etaria ≤ ciclo_vida`

**20. A `dim_estabelecimento` tem duas hierarquias. Quais e por quê?**
`cnes ≤ tipo_unidade ≤ nivel_atencao` (classificação funcional) e `cnes ≤ bairro ≤ municipio ≤ regiao_imediata ≤ uf` (geográfica). São caminhos de agregação independentes: dá para subir por tipo de unidade sem passar pela geografia e vice-versa.

**21. Na `dim_perfil_paciente`, por que o sexo não está na hierarquia?**
Porque sexo e faixa etária são independentes: nenhuma faixa etária "pertence" a um sexo. O sexo é um atributo descritivo, e a hierarquia é só `faixa_etaria ≤ ciclo_vida`.

---

## Nível 3: constelação e consultas OLAP

**22. O que é uma constelação de fatos?**
É um esquema com várias tabelas de fatos que compartilham dimensões. Aqui, as três tabelas de fatos compartilham tempo e estabelecimento, e as de internação e produção também compartilham procedimento, perfil do paciente e localidade.

**23. O que é dimensão conforme? Como vocês garantiram isso?**
É uma dimensão com a mesma chave, os mesmos atributos e os mesmos valores em todas as estrelas que a usam. Nós garantimos isso na integração. O tempo é sempre o mês de competência em AAAAMM, o sexo é sempre M/F/I, o CNES sempre tem 7 dígitos e o município sempre tem 6 dígitos, com o nome vindo do IBGE. Sem isso, o drill-across não funcionaria.

**24. Descreva o processo de projeto da constelação.**
Primeiro, cada processo foi modelado como uma estrela independente. Depois, identificamos as dimensões que aparecem em mais de uma estrela, e cada uma delas ganhou uma definição única (conformação). Por fim, as três tabelas de fatos passaram a apontar para as mesmas tabelas de dimensão. A matriz de barramento (dimensão × fato) no relatório resume o resultado.

**25. Por que o grão do tempo é o mês e não o dia?**
Porque o mês é o menor nível comum às três fontes. O CNES é um cadastro mensal, o SIA vem agregado por mês e o SIH tem datas de internação, mas é organizado por competência. Para conformar o tempo entre os três fatos, o mês é o grão possível.

**26. Explique cada uma das 5 consultas e a operação OLAP.**
1. **Roll-up:** ICSAP de residentes por mês, agregado para trimestre e depois para ano. Sobe na hierarquia do tempo. Resultado: 5.255 ICSAP no período (16% das 32.799 internações de residentes); 2.700 em 2023 e 2.555 em 2024, queda de cerca de 5%.
2. **Drill-down:** produção ambulatorial aprovada em estabelecimentos de São Carlos por grupo, depois por subgrupo do grupo maior e depois por procedimento. Desce na hierarquia do procedimento. O grupo 02 (diagnóstico) lidera em quantidade (1,77 milhão), puxado pelo laboratório clínico (0202); hemograma completo é o procedimento mais frequente.
3. **Slice and dice:** slice em ano = 2024 e dice em ciclo de vida = Idoso e ICSAP = Sim, analisando por causa e sexo. Foram 1.358 ICSAP de idosos em 2024, lideradas pelas doenças cerebrovasculares e pela insuficiência cardíaca.
4. **Pivot:** ICSAP por causa (linhas) × ciclo de vida (colunas) e a mesma visão com os eixos trocados. Nas crianças predominam as doenças pulmonares (329) e a asma (159).
5. **Drill-across:** combina as três tabelas de fatos por mês: equipes eSF e cobertura estimada, produção APS no SIA e taxa de ICSAP por 10 mil habitantes. É a pergunta central do trabalho.

**27. Qual a diferença entre slice e dice?**
O slice fixa um único valor de uma dimensão e reduz o cubo em uma dimensão (aqui, ano = 2024). O dice seleciona um subcubo com restrições em duas ou mais dimensões (aqui, ciclo de vida = Idoso e ICSAP = Sim). Na Consulta 3 as duas operações aparecem juntas.

**28. O pivot muda o resultado da consulta?**
Não. Os números são os mesmos, só a orientação muda. O ganho é de leitura: com causa nas linhas, a pergunta é "em que fase da vida cada causa pesa?"; com ciclo de vida nas linhas, é "quais causas pesam em cada fase?". A primeira serve a linhas de cuidado por doença, a segunda a programas por público (saúde da criança, do idoso).

**29. Como o drill-across é executado em SQL? Por que não fazer um JOIN direto entre as tabelas de fatos?**
Cada tabela de fatos é agregada **separadamente** por `ano_mes`, e só depois os três resultados são combinados pelo mês. Um JOIN direto entre fatos com grãos diferentes multiplicaria linhas (fan-out). Cada equipe seria repetida para cada internação do mesmo mês, e as contagens e somas sairiam infladas. A dimensão conforme (tempo) é o que permite alinhar os resultados agregados.

**30. Como se calcula a cobertura estimada? Quanto deu?**
Equipes eSF × 3.450 pessoas ÷ população × 100, com limite de 100%. O parâmetro de 3.450 pessoas por equipe é o usado historicamente pelo Ministério da Saúde. São Carlos teve 23 eSF em todos os 24 meses: 23 × 3.450 ÷ 254.857 ≈ **31,1%**.

**31. E a taxa de ICSAP por 10 mil habitantes?**
Internações ICSAP de residentes ÷ população × 10.000. Variou entre 6,55 (jan/2024, 167 internações) e 11,42 (dez/2023, 291), terminando 2024 em 8,40.

**32. Por que a taxa de aprovação não é armazenada na tabela de fatos?**
Porque ela é não aditiva. Se ficasse armazenada, alguém poderia somá-la ou tirar média simples entre linhas, o que dá errado: a média de taxas não pondera pelo volume. O certo é calcular `SOMA(qtd_aprovada) ÷ SOMA(qtd_apresentada)` no nível de agregação da consulta.

---

## Nível 4: ETL, integração e qualidade dos dados

**33. Que conflitos de integração vocês encontraram entre as fontes?**
- **Sexo:** no SIH, 1 = masculino e 3 (ou 2) = feminino; no SIA, M/F. No DW fica M, F, I.
- **Idade:** no SIH vem valor + unidade (`COD_IDADE`: dias, meses, anos, centenas de anos); no SIA vem em anos. O DW converte tudo para anos e depois para faixa etária, e menores de 1 ano entram em 00-04.
- **Município:** o DATASUS usa 6 dígitos e o IBGE usa 7 (com dígito verificador). O DW guarda 6 dígitos, com o nome vindo do IBGE.
- **Competência:** no SIH, ano e mês ficam em colunas separadas; no SIA e no CNES vêm como AAAAMM.
- **Tipo de unidade:** no CNES-ST é texto ("02"); na API é inteiro (2).
- **CNES:** às vezes chega sem zeros à esquerda; no DW é texto com 7 dígitos.

**34. O que é uma AIH de continuação e por que vocês a descartam?**
Internações muito longas geram AIHs adicionais nos meses seguintes (`IDENT = 5`). Se ficassem, a mesma internação seria contada mais de uma vez. Por isso o grão "uma internação" exige descartá-las.

**35. Como vocês validaram que a carga está certa?**
Comparando com o TabNet do DATASUS, que é independente do nosso código:
- AIHs de residentes em jan/2024: 1.287 no TabNet e 1.285 no DW. A diferença corresponde exatamente às AIHs de continuação descartadas.
- Em abr/2023 e dez/2024, a diferença foi de 1 AIH em cerca de 1.400.
- O capítulo IX da CID (doenças do aparelho circulatório) em jan/2024 bateu exatamente.

Também conferimos a lista de ICSAP com o texto da Portaria 221/2008 e os códigos de tipo de equipe com o `EQUIPE.dbf` do TAB_CNES.

**36. Quais erros apareceram quando o ETL rodou com dados reais?**
Vários, e todos foram corrigidos:
- A coluna de equipe se chama `IDEQUIPE`, e não `ID_EQUIPE`.
- `DT_DESAT` vem como AAAAMM, e 900001 significa "nunca desativada".
- No SIA, a competência certa é `PA_MVM` (mês de processamento).
- O PySUS devolveu lista vazia em 5 meses do SIH, então criamos um fallback direto no FTP.
- Faltavam tipos de unidade (67, 76, 80) e códigos de equipe (04, 22, 23).

Rodar com dados reais foi o que expôs esses problemas; o modelo teórico não teria mostrado nenhum deles.

**37. Por que usar `PA_MVM` (processamento) e não `PA_CMP` (atendimento) no SIA?**
Para manter o mesmo critério dos outros fatos, que usam a competência, que também é a forma como o Ministério tabula os dados. Além disso, produção apresentada com atraso teria `PA_CMP` antigo e cairia em meses fora do período carregado. O custo é que o mês do DW é o mês de processamento, não necessariamente o do atendimento. A oscilação mensal da Consulta 1 reflete em parte o ritmo de apresentação dos hospitais.

**38. Como vocês tratam equipes desativadas?**
O arquivo EP do CNES pode listar equipes já desativadas. Só entram no fato as equipes sem data de desativação (900001) ou com desativação posterior ao mês da competência.

---

## Nível 5: perguntas difíceis e críticas ao modelo

**39. A Consulta 5 mostra produção APS igual a zero em todos os meses. Isso não é um erro do ETL?**
Não. Desde o e-SUS APS, a produção das UBS/USF vai para o **SISAB**, não para o SIA. Conferimos que as unidades de atenção primária de São Carlos não têm nenhum procedimento no SIA em 2023 e 2024, enquanto o restante da rede tem 193 mil linhas de produção. O painel zerado é um achado sobre a fonte, não uma falha da carga, e o relatório explica isso na Seção 1.6. Na prática, a estrela de produção ambulatorial descreve a atenção especializada, diagnóstica e de urgência. Se a parte 2 quiser medir a produção da APS, o SISAB entra como fonte nova.

**40. Se as equipes ficaram constantes em 23, o drill-across prova alguma coisa?**
Não prova relação causal, e nós não afirmamos que prova. A consulta mostra que o modelo responde à pergunta: as três tabelas de fatos se alinham pelo mês. Os dados de 2023–2024 é que não têm variação na oferta para correlacionar com a ICSAP. Para isso seria preciso uma série mais longa (por exemplo, desde 2015) ou um recorte por território, e mesmo assim correlação não seria causalidade.

**41. A cobertura estimada de 31,1% é a cobertura oficial?**
Não. É uma aproximação com o parâmetro fixo de 3.450 pessoas por equipe. A metodologia oficial do Ministério mudou ao longo dos anos (cobertura por equipe, depois por cadastro no Previne Brasil, depois os novos indicadores de 2024). Além disso, o cálculo não inclui as eAP nem as UBS tradicionais sem eSF. Usamos o número como indicador de tendência, não como valor oficial.

**42. Calcular a taxa mensal de ICSAP com a população do Censo 2022 é correto?**
É uma simplificação. A população muda um pouco entre 2023 e 2024, e o ideal seria usar as estimativas anuais do IBGE ou uma dimensão de população por ano. Como a variação é pequena em dois anos, o impacto nas comparações mês a mês é desprezível. Outra observação: a taxa mensal fica na escala de 6 a 11 por 10 mil; a taxa anual, que é a usual na literatura, fica perto de 100 por 10 mil.

**43. A `dim_perfil_paciente` é mesmo uma mini-dimensão no sentido de Kimball?**
A mini-dimensão clássica separa atributos que mudam com frequência de uma dimensão grande (por exemplo, a faixa de renda de uma dimensão cliente com milhões de linhas). Aqui não existe dimensão paciente, porque os microdados públicos do SUS não identificam o paciente. Então a `dim_perfil_paciente` usa a mesma técnica (uma dimensão pequena com todas as combinações de sexo × faixa etária, ligada direto ao fato), mas não "sai" de uma dimensão maior. Se a banca questionar, essa é a resposta honesta: é uma dimensão demográfica construída como mini-dimensão porque não há paciente identificável.

**44. A hierarquia `bairro ≤ municipio` é estrita? Existe "Centro" em várias cidades.**
O nome do bairro não é único, mas o par (município, bairro) é. Num roll-up correto, o bairro é agrupado junto com o município, ou ganha uma chave composta. Há também uma limitação prática: bairro e coordenadas vêm da API de Dados Abertos, que tem geolocalização imprecisa (várias UBS com a mesma coordenada). Por isso não fizemos análise espacial fina.

**45. O que acontece se uma UBS mudar de tipo ou um hospital mudar de gestão? O modelo guarda histórico?**
Não guarda. A `dim_estabelecimento` funciona como SCD tipo 1, e o valor atual sobrescreve o anterior. Em dois anos essas mudanças são raras. Se fossem relevantes, a solução seria SCD tipo 2: uma nova linha com nova `sk_estabelecimento` e vigência, e é exatamente para permitir isso que existem as chaves artificiais. Ficou fora do escopo porque o grupo preferiu fazer o básico bem feito.

**46. `dim_procedimento` está nas estrelas de internação e de produção. A mesma hierarquia serve para as duas?**
Sim. SIH e SIA usam a mesma Tabela SUS (SIGTAP), com o código de 10 dígitos, então a dimensão é conforme de verdade. Os grupos do SIGTAP também separam bem os dois mundos: os procedimentos cirúrgicos (grupo 04) aparecem mais nas internações e os diagnósticos (grupo 02) no ambulatório.

**47. Por que o grão de `fato_producao_ambulatorial` inclui o CBO? Isso não deixa a tabela grande demais?**
Porque o arquivo PA já traz o CBO, e ele permite perguntas sobre quem atende (médico, enfermeiro, agente comunitário). Com 193.723 linhas para dois anos de um município, o tamanho é pequeno. O cuidado é que o grão define a granularidade máxima: se tivéssemos agregado sem o CBO na carga, essa pergunta nunca mais poderia ser feita sem voltar à fonte.

**48. Uma ICSAP de um morador de São Carlos internado em Ribeirão Preto entra em qual consulta?**
Entra nas consultas de demanda (1, 3, 4 e na parte ICSAP da 5), que filtram por **residência**, porque o paciente é parte da população de São Carlos. Ela não entra numa consulta sobre a rede hospitalar de São Carlos, que filtra pelo município do **estabelecimento**. É para isso que existem duas dimensões geográficas diferentes: `dim_localidade` (residência) e a geografia da `dim_estabelecimento`.

**49. A lista de ICSAP usa só o diagnóstico principal. Isso subestima ou superestima?**
A Portaria 221/2008 é aplicada ao diagnóstico principal da AIH, que é o padrão da literatura brasileira. Isso evita contar duas vezes, mas pode subestimar casos em que a condição sensível aparece só como diagnóstico secundário. Seguimos o padrão para que o número seja comparável com outros estudos e com o TabNet.

**50. Se tivessem de implementar isso em produção para a prefeitura, o que mudariam?**
- Incluir o **SISAB** como fonte, para medir a produção real da APS.
- Usar população por ano (estimativas do IBGE) e, se possível, por território de UBS.
- Usar SCD tipo 2 na `dim_estabelecimento`.
- Usar uma série mais longa, para que o drill-across tenha variação de oferta.
- Automatizar a carga mensal e manter a conferência contra o TabNet como teste de regressão.

---

## Dicas rápidas para a apresentação

- Quando perguntarem sobre a produção APS zerada ou a cobertura constante, trate isso como **achado**, não como desculpa: o DW serviu justamente para mostrar esses problemas nas fontes.
- Tenha os números de cabeça: 254.857 habitantes, 23 eSF, 31,1% de cobertura, 5.255 ICSAP (16%), 1.285 contra 1.287 no TabNet.
- Se não souber responder, diga o que o modelo faz hoje e o que mudaria (perguntas 45 e 50). Uma limitação admitida com plano de correção pesa menos do que uma resposta inventada.
