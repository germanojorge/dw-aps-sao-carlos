# Parte 3: Constelação e integração

Apresentador: Germano Jorge · slides 13 a 18 · cerca de 5 minutos

A parte 3 explica como as três estrelas viram um DW só e por que isso permite a pergunta central. É também onde aparecem as decisões técnicas que a professora mais costuma cobrar: dimensões conformes, integração, hierarquias e os aspectos de modelagem.

## Slide 13 · Abertura: constelação e integração

**O que o slide mostra.** O divisor da parte 3.

**A aula.** Até aqui cada processo foi modelado sozinho. Só que três estrelas isoladas são três bancos separados: não dá para cruzar oferta com internações. Esta parte mostra o que liga as estrelas (as dimensões compartilhadas) e o trabalho necessário para que elas possam ser compartilhadas (a integração dos dados).

**Fala de exemplo**

> “O Vinícius mostrou três estrelas separadas. Agora eu vou mostrar como elas viram uma coisa só, e o que a gente teve que fazer com os dados pra isso funcionar.”

## Slide 14 · Constelação de fatos

**O que o slide mostra.** Os três fatos (em azul) ligados às dimensões; as dimensões com borda grossa são compartilhadas. Embaixo, os quatro passos do projeto.

**A aula.** Uma **constelação de fatos** (ou esquema galáxia) é um esquema com várias tabelas de fatos que compartilham tabelas de dimensão. Ela foi obtida em quatro passos:

1. **Estrelas separadas**: cada processo modelado com seu grão, fatos e dimensões.
2. **Dimensões em comum**: comparando as estrelas, aparecem as que se repetem.
3. **Conformar**: cada dimensão comum passa a ter uma única definição, com a mesma chave, os mesmos atributos e os mesmos valores em todos os fatos.
4. **Ligar os fatos**: os três fatos apontam para as mesmas tabelas de dimensão.

O passo 3 é o coração: uma **dimensão conforme** é aquela que significa exatamente a mesma coisa em todos os fatos. Por exemplo, o tempo usa sempre o mês, e “mês” tem o mesmo significado nas três fontes. Foi por isso que o grão do tempo foi fixado no mês: é o menor nível que as três fontes têm em comum.

**Como se liga ao trabalho.** As compartilhadas são tempo, estabelecimento, procedimento, perfil do paciente e localidade. O enunciado pede pelo menos uma constelação; é ela que torna possível a consulta 5.

**Fala de exemplo**

> “Isso aqui é a constelação de fatos: os três fatos, em azul, apontando pras mesmas dimensões. A gente chegou nela em quatro passos: modelou cada estrela separada, viu quais dimensões se repetiam, conformou essas dimensões e aí ligou tudo. Conformar é a parte importante: quer dizer que, por exemplo, o tempo é exatamente a mesma tabela, com a mesma chave e o mesmo significado, nos três fatos. Por isso a gente fixou o tempo no mês, que é o menor nível que as três fontes têm em comum. As dimensões com borda grossa são as compartilhadas.”

## Slide 15 · Quem usa o quê

**O que o slide mostra.** Uma matriz com as dimensões nas linhas e os fatos nas colunas; as cinco primeiras linhas (destacadas) são as dimensões conformes.

**A aula.** Essa é a **matriz de barramento** (bus matrix) do Kimball: a forma mais rápida de ver a arquitetura de um DW. Cada coluna é um processo; cada linha é uma dimensão; uma marca diz que o fato usa aquela dimensão.

| Dimensão | fato\_equipe | fato\_internacao | fato\_producao |
| --- | --- | --- | --- |
| tempo | ✓ | ✓ | ✓ |
| estabelecimento | ✓ | ✓ | ✓ |
| procedimento |  | ✓ | ✓ |
| perfil do paciente |  | ✓ | ✓ |
| localidade |  | ✓ | ✓ |
| tipo de equipe | ✓ |  |  |
| diagnóstico |  | ✓ |  |
| bugiganga |  | ✓ |  |
| ocupação (CBO) |  |  | ✓ |

Lendo pelas linhas: uma dimensão que aparece em mais de um fato precisa ser conforme. Lendo pelas colunas: cada coluna é uma estrela da parte 2.

**Como se liga ao trabalho.** Só tempo e estabelecimento aparecem nos três fatos. Então são eles o “caminho” por onde os três processos podem ser comparados: a consulta 5 junta os fatos pelo mês e filtra pelo município.

**Fala de exemplo**

> “A mesma coisa em forma de matriz, que é a matriz de barramento: nas linhas as dimensões, nas colunas os fatos. As cinco de cima aparecem em mais de um fato, então são as conformes. E repara que só tempo e estabelecimento aparecem nos três. Isso é importante: é por elas que dá pra comparar equipes, atendimentos e internações na mesma análise, que é o que o Matheus vai fazer no drill-across.”

## Slide 16 · Mesmo dado, códigos diferentes

**O que o slide mostra.** Cinco dados que chegam com representações diferentes de duas fontes, e a representação escolhida no DW.

**A aula.** **Integração** é resolver os conflitos quando o mesmo dado chega de fontes diferentes com códigos diferentes. Sem isso, a dimensão não pode ser conforme: “feminino” no SIH e “feminino” no SIA precisam virar o mesmo valor.

| Dado | Fonte A | Fonte B | No DW |
| --- | --- | --- | --- |
| Sexo | SIH: 1 = masculino, 3 = feminino | SIA: M, F | M, F, I (ignorado) |
| Idade | SIH: valor + unidade (dias, meses, anos) | SIA: anos | faixa etária e ciclo de vida |
| Município | DATASUS: 6 dígitos | IBGE: 7 dígitos (com dígito verificador) | 6 dígitos, nome do IBGE |
| CNES | às vezes sem os zeros à esquerda | API: número inteiro | texto com 7 dígitos |
| Competência | SIH: ano e mês separados | SIA e CNES: AAAAMM | ano\_mes (AAAAMM) |

O exemplo da idade mostra por que não dá para usar o campo direto: no SIH, “7” com unidade “meses” é um bebê de 7 meses, que no SIA aparece como 0 anos. Os dois viram a faixa 00-04 e o ciclo “Criança”.

**Como se liga ao trabalho.** Ao rodar com dados reais, a integração funcionou: todas as chaves estrangeiras dos três fatos foram resolvidas. Ela também mostrou a qualidade da fonte: cerca de 6% das linhas brutas do SIA chegam sem sexo informado, e vão para o valor “I”. Um ajuste extra: no SIA usamos o mês de processamento (`PA_MVM`), que é o mesmo critério de competência do SIH.

**Fala de exemplo**

> “Mas pra conformar as dimensões, os dados têm que falar a mesma língua, e eles não falam. O sexo, por exemplo: no SIH é 1 e 3, no SIA é M e F. No DW fica M, F e I de ignorado. A idade é pior: o SIH manda um número mais uma unidade, então 7 meses vem como ‘7 meses’, e o SIA manda 0 anos. Os dois viram a faixa de 0 a 4 anos, criança. Município tem 6 dígitos no DATASUS e 7 no IBGE, o CNES às vezes perde o zero da frente, e a competência vem separada no SIH. E funcionou: com os dados reais, todas as chaves foram resolvidas.”

## Slide 17 · Hierarquias (≤)

**O que o slide mostra.** Três hierarquias: tempo, diagnóstico (duas) e procedimento (no próprio código SIGTAP).

**A aula.** Uma **hierarquia** organiza os atributos de uma dimensão do mais detalhado ao mais agregado. A notação usa o operador de ordem parcial: `A ≤ B` quer dizer que A é mais detalhado que B e que cada valor de A pertence a um único valor de B. As hierarquias são o “trilho” das operações de roll-up (subir) e drill-down (descer).

- **Tempo**: `ano_mes ≤ trimestre ≤ semestre ≤ ano`.
- **Diagnóstico** tem duas hierarquias na mesma dimensão. A da CID-10: `J181 ≤ J18 ≤ capítulo X` (subcategoria, categoria, capítulo). A das ICSAP: `J181 ≤ pneumonias bacterianas ≤ ICSAP sim`. Um mesmo código sobe por dois caminhos diferentes.
- **Procedimento**: o código SIGTAP de 10 dígitos já é hierárquico. Os 2 primeiros dígitos são o grupo, os 4 primeiros o subgrupo, os 6 primeiros a forma de organização, e o código inteiro o procedimento.

**Como se liga ao trabalho.** Cada consulta anda por uma dessas hierarquias: a consulta 1 sobe no tempo (mês, trimestre, ano) e a consulta 2 desce no procedimento (grupo, subgrupo, procedimento).

**Fala de exemplo**

> “As dimensões têm hierarquias, e a gente usa a notação com o menor ou igual: A ≤ B quer dizer que A é mais detalhado e cada A cabe em um único B. No tempo é o óbvio: mês, trimestre, semestre, ano. O diagnóstico é o mais interessante, porque tem duas: a da CID, que vai do código até o capítulo, e a das ICSAP, que vai do código até o grupo e até ‘é ICSAP ou não’. E no procedimento a hierarquia tá dentro do próprio código do SIGTAP: os dois primeiros dígitos são o grupo, os quatro o subgrupo, e assim vai. É por esses trilhos que o roll-up e o drill-down andam.”

## Slide 18 · Decisões de modelagem

**O que o slide mostra.** Seis cartões com as decisões de modelagem do DW.

**A aula.** Cada cartão é um conceito clássico de modelagem dimensional:

- **Chave artificial** (`sk_*`): toda dimensão tem uma chave própria, sem significado, gerada na carga. Isso isola o DW dos códigos das fontes, que mudam e às vezes vêm com problemas. Toda dimensão tem também um membro 0 “Não informado”: quando a fonte não traz o valor, o fato aponta para o 0 em vez de ser perdido.
- **Tabela bugiganga** (`dim_junk`): caráter, óbito e UTI numa dimensão só.
- **Dimensão degenerada** (`n_aih` e `id_equipe`): identificadores que ficam no fato, sem tabela própria.
- **Fato sem fato** (`COUNT(*)`): `fato_equipe` registra só a existência de uma equipe ativa num mês.
- **Mini-dimensão** (sexo × faixa etária): o paciente do SUS não tem identificação pública, então não existe uma dimensão “paciente”. Os atributos demográficos viram uma dimensão pequena, com uma linha por combinação, compartilhada pelos fatos.
- **Demanda ≠ oferta**: as consultas sobre a população filtram pelo município de **residência**; as sobre a rede instalada filtram pelo município do **estabelecimento**.

**Como se liga ao trabalho.** Os quatro primeiros são os aspectos que o enunciado pede; os dois últimos são decisões nossas. A última pesa nos números: nos dados brutos, cerca de 6,8 mil internações em São Carlos são de quem mora em outra cidade, e cerca de 3,3 mil moradores foram internados fora. Por isso a demanda filtra por residência: a pergunta é sobre a população de São Carlos, onde quer que ela tenha sido atendida.

**Fala de exemplo**

> “Pra fechar a minha parte, as decisões de modelagem. Toda dimensão tem chave artificial e um membro zero, ‘não informado’, pra nenhum fato se perder quando falta dado. Tem a bugiganga e as dimensões degeneradas que o Vinícius mostrou, e o fato sem fato das equipes. A mini-dimensão de perfil existe porque o paciente do SUS não tem identificação pública, então o que a gente tem é sexo e faixa etária. E uma que mexe muito nos números: demanda é diferente de oferta. Uns 6,8 mil internados em São Carlos moram em outra cidade, então quando a pergunta é sobre a população, a gente filtra por onde a pessoa mora. Agora o Matheus mostra as consultas.”

## Lembretes

- As explicações são para estudar antes: leiam a parte de vocês e também a dos outros, porque a professora pode perguntar qualquer coisa a qualquer um.
- As falas têm de 40 segundos a 1 minuto por slide. Não decorem palavra por palavra: guardem a ideia e os números.
- Os números citados são os resultados reais do notebook (dados de 2023 e 2024). As mesmas falas, em versão curta, estão nas notas do apresentador (tecla N na apresentação).
