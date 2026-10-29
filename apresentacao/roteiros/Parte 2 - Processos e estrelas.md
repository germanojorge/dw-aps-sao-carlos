# Parte 2: Processos e estrelas

Slides 7 a 11 · cerca de 5 minutos

A parte 2 mostra como cada peça da pergunta virou um esquema estrela. É a parte mais “de modelagem”: grão, medidas e dimensões de cada fato, e os cuidados com o que pode e o que não pode ser somado.

## Slide 7 · Abertura: três processos de negócio

**O que o slide mostra.** O divisor da parte 2.

**A aula.** Na modelagem dimensional (Kimball), um **processo de negócio** é uma atividade que gera eventos mensuráveis: uma venda, uma matrícula, uma internação. Cada processo vira uma tabela de fatos, cercada pelas dimensões que descrevem esses eventos. Os nossos três processos são os três ângulos da pergunta central: a oferta de equipes, as internações e os atendimentos ambulatoriais.

**Como se liga ao trabalho.** O enunciado pede pelo menos 3 processos e 2 esquemas estrela; temos 3 processos, 3 estrelas.

**Fala de exemplo**

> “Beleza, agora eu vou mostrar como a gente transformou essa pergunta em modelo. São três processos de negócio, um pra cada peça da pergunta: oferta de equipes, internações e atendimentos.”

## Slide 8 · Focos de interesse

**O que o slide mostra.** Os três data marts na notação vista em aula: Demanda, Foco e Perspectivas.

**A aula.** A notação da aula descreve cada data mart em três partes. A **demanda** é a necessidade do usuário (“acompanhar a oferta de equipes”). O **foco** é o que se mede, ou seja, as medidas que vão para a tabela de fatos. As **perspectivas** são os ângulos de análise, que viram as dimensões.

| Data mart | Foco (medidas) | Perspectivas (dimensões) |
| --- | --- | --- |
| 1 – Oferta de equipes | nº de equipes | estabelecimento, tipo de equipe, mês |
| 2 – Internações | internações, dias, valor | diagnóstico, paciente, residência, hospital, procedimento, mês |
| 3 – Atendimentos | quantidade e valor aprovados | procedimento, profissional, paciente, residência, estabelecimento, mês |

**Como se liga ao trabalho.** Esse slide é a ponte entre a pergunta (parte 1) e as estrelas (próximos slides): cada linha da tabela vira um esquema. Repare que “mês” aparece nos três: é a semente da dimensão tempo compartilhada.

**Fala de exemplo**

> “Na notação que a gente viu em aula, cada data mart tem uma demanda, um foco e as perspectivas. O primeiro é a oferta de equipes: o foco é o número de equipes, olhando por estabelecimento, tipo de equipe e mês. O segundo são as internações: quantas, quantos dias e quanto custaram, por diagnóstico, paciente, onde a pessoa mora e assim vai. O terceiro são os atendimentos ambulatoriais. O foco vira a tabela de fatos e as perspectivas viram as dimensões. E olha que o mês aparece nos três, isso vai ser importante depois.”

## Slide 9 · Estrela 1: oferta de equipes

**O que o slide mostra.** O esquema estrela de `fato_equipe` com três dimensões (tempo, tipo de equipe, estabelecimento).

**A aula.** O primeiro passo de qualquer estrela é definir o **grão**: o que uma linha da tabela de fatos representa. Aqui, uma linha é “uma equipe ativa, num estabelecimento, num mês”. É um **snapshot periódico**: uma fotografia mensal de quais equipes existem.

Essa tabela não tem nenhuma medida numérica, por isso é uma **tabela de fatos sem fato** (factless). O número de equipes sai da contagem de linhas, `COUNT(*)`. O identificador da equipe (`IDEQUIPE`, no CNES) fica dentro do próprio fato como **dimensão degenerada**: é um código sem outros atributos, que não justifica uma tabela própria, mas serve para contar equipes distintas e rastrear a origem.

A dimensão tipo de equipe tem a hierarquia `tipo_equipe ≤ categoria_equipe` (Saúde da Família, Atenção Primária, Saúde Bucal, Multiprofissional, Outras). Os códigos de tipo foram conferidos com a tabela oficial do CNES.

A contagem de equipes é **semiaditiva**. Medidas têm três comportamentos diante da soma: **aditivas** somam em todas as dimensões (ex.: dias de internação); **semiaditivas** somam em algumas, mas não em outras (o caso típico de snapshots: saldo de conta, estoque, número de equipes); **não aditivas** não somam em nenhuma (ex.: taxas e médias). Somar equipes entre estabelecimentos ou tipos faz sentido, porque são equipes diferentes. Somar janeiro com fevereiro conta a mesma equipe duas vezes. Para agregar no tempo usa-se a média do período ou o valor do último mês. Se alguém fizesse um roll-up de mês para ano com SOMA, São Carlos teria “276 equipes” em 2023 (23 × 12), o que não existe; por isso, na consulta 5, o fato de equipes é sempre lido mês a mês.

**Como se liga ao trabalho.** É a “oferta” da pergunta central. Um cuidado da carga: o CNES pode listar equipes já desativadas, então filtramos pela data de desativação (`DT_DESAT`, que vem no formato ano-mês). Com os dados reais, a tabela ficou com 1.686 linhas, e São Carlos teve 23 equipes de Saúde da Família em todos os meses.

**Fala de exemplo**

> “A primeira estrela é a da oferta de equipes, que vem do CNES. O grão, ou seja, o que cada linha representa, é uma equipe ativa num estabelecimento num mês, tipo uma fotografia mensal. E o legal é que essa tabela não tem medida nenhuma: é o que se chama de fato sem fato. Pra saber quantas equipes tem, a gente só conta as linhas. O código da equipe fica dentro do fato como dimensão degenerada, porque ele não tem outros atributos que justifiquem uma tabela só pra ele. E essa contagem é semiaditiva: dá pra somar entre estabelecimentos e tipos de equipe, mas no tempo não, senão a mesma equipe conta duas vezes. No tempo a gente usa a média ou o último mês. Com os dados reais deu 1.686 linhas, e São Carlos teve 23 equipes de Saúde da Família em todos os meses.”

## Slide 10 · Estrela 2: internações

**O que o slide mostra.** O esquema de `fato_internacao` com sete dimensões.

**A aula.** Aqui o grão é o mais fino possível: **uma AIH**, ou seja, uma internação. As medidas são `qtd_internacoes` (sempre 1, para facilitar a contagem), `dias_permanencia` e `valor_total`, todas **aditivas**. A média de permanência é **derivada e não aditiva**: calcula-se como soma dos dias dividida pela soma das internações, nunca somando médias.

As dimensões são tempo, estabelecimento (o hospital), localidade (o município de residência do paciente), perfil do paciente (sexo × faixa etária), diagnóstico (CID-10, capítulo e grupo ICSAP), procedimento (tabela SIGTAP) e a **tabela bugiganga** (junk). A bugiganga junta três flags pequenas e sem relação entre si (caráter do atendimento, óbito, UTI) numa dimensão só, com uma linha por combinação. Isso evita três dimensões minúsculas ou três colunas soltas no fato. O número da AIH fica no fato como dimensão degenerada.

**Como se liga ao trabalho.** É o “resultado” da pergunta. Um cuidado importante: internações muito longas geram AIHs de continuação (identificação tipo 5) nos meses seguintes; elas são descartadas para a mesma internação não contar duas vezes. O DW ficou com 39.609 internações (moradores de São Carlos ou internados na cidade), das quais 32.799 são de residentes.

**Fala de exemplo**

> “A segunda estrela são as internações, que vêm do SIH. Aqui o grão é uma AIH, que é uma internação. As medidas são quantidade, dias de permanência e valor, e dá pra somar todas. Já a média de permanência não: ela é calculada, soma dos dias dividida pela soma das internações. Uma coisa que eu acho bem legal aqui é a tabela bugiganga: caráter do atendimento, se teve óbito e se passou pela UTI são três informaçõezinhas soltas, então a gente juntou numa dimensão só. E as AIHs de continuação, de internação muito longa, a gente descarta pra não contar a mesma pessoa duas vezes. No total foram umas 39 mil internações.”

## Slide 11 · Estrela 3: produção ambulatorial

**O que o slide mostra.** O esquema de `fato_producao_ambulatorial` com seis dimensões.

**A aula.** O arquivo público do SIA já vem **parcialmente agregado**: cada linha conta quantos procedimentos iguais um estabelecimento fez num mês, para pacientes de um mesmo perfil e município, por profissionais de uma mesma ocupação. Por isso o grão não é “um atendimento”, mas a combinação estabelecimento × procedimento × mês × perfil × residência × CBO. O modelo não pode ser mais detalhado do que a fonte.

São quatro medidas aditivas: quantidade e valor **apresentados** (o que o estabelecimento informou) e **aprovados** (o que o SUS aceitou pagar). A taxa de aprovação é derivada e não aditiva: soma do aprovado dividida pela soma do apresentado. Somar taxas de vários estabelecimentos daria um número sem sentido.

A dimensão CBO (Classificação Brasileira de Ocupações) diz quem fez o atendimento (médico, enfermeiro etc.). A dimensão procedimento segue a tabela SIGTAP, cuja hierarquia é usada no drill-down da consulta 2.

**Como se liga ao trabalho.** É o “uso” da pergunta. A tabela ficou com 193.723 linhas. Um ajuste feito com os dados reais: o mês usado é o de processamento (`PA_MVM`), para que produção apresentada com atraso não caia fora do período. E, como a parte 4 vai mostrar, as UBS de São Carlos não aparecem nessa base: a produção delas vai para outro sistema, o SISAB.

**Fala de exemplo**

> “A terceira estrela é a produção ambulatorial, do SIA. Aqui tem um detalhe: o arquivo público já vem meio agregado, então cada linha não é um atendimento, é tipo ‘tantos procedimentos iguais, nesse lugar, nesse mês, pra esse perfil de paciente’. Por isso o grão ficou esse combinão: estabelecimento, procedimento, mês, perfil, residência e ocupação do profissional. As medidas são quantidade e valor, apresentados e aprovados. E a taxa de aprovação a gente nunca soma: é sempre soma do aprovado dividido pela soma do apresentado. Agora vamos ver como essas três estrelas viram uma coisa só.”

## Lembretes

- As explicações são para estudar antes: leiam a parte de vocês e também a dos outros, porque a professora pode perguntar qualquer coisa a qualquer um.
- As falas têm de 40 segundos a 1 minuto por slide. Não decorem palavra por palavra: guardem a ideia e os números.
- Os números citados são os resultados reais do notebook (dados de 2023 e 2024). As mesmas falas, em versão curta, estão nas notas do apresentador (tecla N na apresentação).
