# Especificação dos esquemas – Cobertura da Atenção Básica em São Carlos

Legenda dos diagramas: **PK** chave primária artificial (*surrogate key*), **FK** chave estrangeira, **DD** dimensão degenerada, **M** medida.
Hierarquias usam o operador de ordenação parcial ≤ (o nível à esquerda é mais detalhado que o da direita).
Toda dimensão tem uma linha com chave 0 ("Não informado") para fatos cujo código não foi encontrado na fonte.

## 1. Dimensões

### dim_tempo
Mês de competência do registro (mês em que o dado foi informado ao Ministério da Saúde).

| Atributo | Significado |
|---|---|
| sk_tempo | chave artificial |
| ano_mes | competência no formato AAAAMM |
| mes, nome_mes | número e nome do mês (descritivos) |
| trimestre, semestre, ano | agrupamentos do calendário |

Hierarquia: `ano_mes ≤ trimestre ≤ semestre ≤ ano`. Atributos só descritivos: `mes`, `nome_mes`.
Fonte: gerada pelo próprio processo de carga a partir do período analisado.

### dim_estabelecimento
Estabelecimento de saúde (UBS, hospital, clínica etc.) identificado pelo código CNES.

| Atributo | Significado |
|---|---|
| sk_estabelecimento | chave artificial |
| cnes | código nacional do estabelecimento (chave natural, 7 dígitos) |
| nome | nome fantasia |
| tipo_unidade_cod, tipo_unidade | tipo do estabelecimento (ex.: 02 = Centro de saúde / Unidade básica) |
| nivel_atencao | Atenção Primária, Especializada, Hospitalar, Urgência ou Outros (derivado do tipo) |
| gestao | gestão municipal, estadual ou dupla |
| bairro, latitude, longitude | localização |
| cod_municipio, municipio, regiao_imediata, uf | localização administrativa |

Hierarquias: `cnes ≤ tipo_unidade ≤ nivel_atencao` e `cnes ≤ bairro ≤ municipio ≤ regiao_imediata ≤ uf`.
Descritivos: `nome`, `gestao`, `latitude`, `longitude`.
Fontes: CNES-ST (DATASUS) para tipo, gestão e município; API de Dados Abertos do Ministério da Saúde para nome, bairro e coordenadas; IBGE para nome do município e região.

### dim_localidade
Município de residência do paciente.

| Atributo | Significado |
|---|---|
| sk_localidade | chave artificial |
| cod_municipio | código IBGE com 6 dígitos |
| municipio | nome |
| regiao_imediata, regiao_intermediaria, uf | divisão regional do IBGE |

Hierarquia: `municipio ≤ regiao_imediata ≤ regiao_intermediaria ≤ uf`. Fonte: API de localidades do IBGE.

### dim_tipo_equipe
Tipo de equipe de saúde cadastrada no CNES.

| Atributo | Significado |
|---|---|
| sk_tipo_equipe | chave artificial |
| tipo_equipe_cod, tipo_equipe | código e descrição (ex.: 70 = eSF) |
| categoria_equipe | agrupamento: Saúde da Família, Atenção Primária, Saúde Bucal, Multiprofissional, Outras |

Hierarquia: `tipo_equipe ≤ categoria_equipe`. Fonte: CNES-EP + tabela de tipos de equipe do CNES.

### dim_procedimento
Procedimento da Tabela SUS (SIGTAP), compartilhada por SIA e SIH.

| Atributo | Significado |
|---|---|
| sk_procedimento | chave artificial |
| cod_procedimento | código de 10 dígitos |
| forma_organizacao_cod, subgrupo_cod, grupo_cod | prefixos de 6, 4 e 2 dígitos do código |
| grupo | nome do grupo (ex.: 03 = Procedimentos clínicos) |

Hierarquia: `cod_procedimento ≤ forma_organizacao_cod ≤ subgrupo_cod ≤ grupo_cod`. Fonte: SIA-PA e SIH-RD (códigos) + SIGTAP (nomes dos grupos).

### dim_diagnostico
Diagnóstico principal da internação (CID-10).

| Atributo | Significado |
|---|---|
| sk_diagnostico | chave artificial |
| cid | código CID-10 com 4 caracteres |
| cid_categoria | 3 primeiros caracteres |
| capitulo_num, capitulo | capítulo da CID-10 |
| icsap | Sim/Não: condição sensível à atenção primária |
| grupo_icsap | um dos 19 grupos da lista brasileira de ICSAP |

Hierarquias: `cid ≤ cid_categoria ≤ capitulo` e `cid ≤ grupo_icsap ≤ icsap`.
Fonte: SIH-RD + CID-10 + Portaria SAS/MS nº 221/2008 (lista de ICSAP).

### dim_perfil_paciente
Combinação de sexo e faixa etária (mini-dimensão, com todas as combinações possíveis).

| Atributo | Significado |
|---|---|
| sk_perfil | chave artificial |
| sexo, sexo_desc | M, F, I (ignorado) e descrição |
| faixa_etaria | 00-04, 05-09, …, 80+, Ignorada |
| ciclo_vida | Criança, Adolescente, Adulto, Idoso |

Hierarquia: `faixa_etaria ≤ ciclo_vida`. `sexo` não se relaciona com a faixa etária.
Fontes: SIH-RD e SIA-PA, que exigem integração (ver seção 4).

### dim_cbo
Ocupação do profissional que realizou o atendimento ambulatorial.

| Atributo | Significado |
|---|---|
| sk_cbo | chave artificial |
| cbo | código da Classificação Brasileira de Ocupações (6 dígitos) |
| familia_cbo | 4 primeiros dígitos |
| categoria_profissional | Médico, Enfermeiro, Agente comunitário etc. |

Hierarquia: `cbo ≤ familia_cbo ≤ categoria_profissional`. Fonte: SIA-PA.

### dim_junk_internacao (tabela bugiganga)
Agrupa indicadores de baixa cardinalidade da internação, que isolados virariam dimensões minúsculas.

| Atributo | Significado |
|---|---|
| sk_junk | chave artificial |
| carater_atendimento | eletivo, urgência, acidentes |
| obito | Sim/Não |
| uti | Sim/Não (passou pela UTI) |

Sem hierarquia; todos descritivos. Contém só as combinações que ocorrem nos dados. Fonte: SIH-RD.

## 2. Fatos

### fato_equipe (tabela de fatos sem fato)
Grão: **uma equipe ativa em um estabelecimento em um mês** (snapshot periódico).
Dimensões: tempo, estabelecimento, tipo de equipe. `id_equipe` é dimensão degenerada.

| Medida | Tipo | Agregação |
|---|---|---|
| (nenhuma) nº de equipes = contagem de linhas | semiaditiva: soma entre estabelecimentos e tipos, mas **não** ao longo do tempo | `COUNT` por mês; entre meses, `MÉDIA` ou último valor |

Fonte: CNES-EP (identificador da equipe: `IDEQUIPE`). Equipes desativadas até o mês são descartadas; `DT_DESAT` vem como AAAAMM e 900001 significa "nunca desativada".

### fato_internacao
Grão: **uma internação (AIH)**. AIHs de continuação de longa permanência são excluídas para não contar a mesma internação duas vezes.
Dimensões: tempo, estabelecimento, procedimento, diagnóstico, perfil do paciente, localidade de residência, bugiganga. `n_aih` é dimensão degenerada.

| Medida | Tipo | Agregação |
|---|---|---|
| qtd_internacoes (sempre 1) | aditiva | SOMA |
| dias_permanencia | aditiva | SOMA (média de permanência é derivada: soma dos dias / qtd_internacoes, não aditiva) |
| valor_total (R$) | aditiva | SOMA |

Fonte: SIH-RD.

### fato_producao_ambulatorial
Grão: **estabelecimento × procedimento × mês × perfil do paciente × município de residência × CBO**. Os registros do SIA já vêm parcialmente agregados; o processo de carga soma os registros com as mesmas chaves.

| Medida | Tipo | Agregação |
|---|---|---|
| qtd_apresentada | aditiva | SOMA |
| qtd_aprovada | aditiva | SOMA |
| valor_apresentado (R$) | aditiva | SOMA |
| valor_aprovado (R$) | aditiva | SOMA |
| taxa de aprovação (derivada, não armazenada) | não aditiva | calculada como SOMA(qtd_aprovada) / SOMA(qtd_apresentada) |

Fonte: SIA-PA.

### Medidas derivadas usadas nas consultas
- **Cobertura estimada de Saúde da Família** = nº de equipes eSF × 3.450 / população; não aditiva.
- **Taxa de ICSAP por 10 mil habitantes** = internações ICSAP / população × 10.000; não aditiva.

## 3. Constelação de fatos

Processo de projeto:
1. Cada processo de negócio (oferta de equipes, internações, produção ambulatorial) foi modelado como uma estrela independente.
2. Foram identificadas as dimensões que aparecem em mais de uma estrela: **tempo**, **estabelecimento**, **procedimento**, **perfil do paciente** e **localidade**.
3. Essas dimensões foram tornadas **conformes**: mesma chave, mesmos atributos e mesmos valores em todas as estrelas. Por exemplo, o tempo usa sempre o mês de competência e o sexo usa sempre M/F/I, qualquer que seja a fonte.
4. As três tabelas de fatos passam a compartilhar essas dimensões, formando a constelação. É isso que permite o drill-across (Consulta 5).

| Dimensão | fato_equipe | fato_internacao | fato_producao_ambulatorial |
|---|:-:|:-:|:-:|
| dim_tempo | ✓ | ✓ | ✓ |
| dim_estabelecimento | ✓ | ✓ | ✓ |
| dim_procedimento | | ✓ | ✓ |
| dim_perfil_paciente | | ✓ | ✓ |
| dim_localidade | | ✓ | ✓ |
| dim_tipo_equipe | ✓ | | |
| dim_diagnostico | | ✓ | |
| dim_junk_internacao | | ✓ | |
| dim_cbo | | | ✓ |

## 4. Integração de dados

| Dado | Fonte A | Fonte B | Representação no DW |
|---|---|---|---|
| Sexo | SIH: 1 = masculino, 3 (ou 2) = feminino | SIA: M, F | M, F, I |
| Idade | SIH: valor + unidade (dias, meses, anos, centenas de anos) | SIA: anos | faixa etária e ciclo de vida |
| Município | DATASUS: 6 dígitos | IBGE: 7 dígitos (com dígito verificador) | 6 dígitos + nome do IBGE |
| Competência | SIH: ANO_CMPT e MES_CMPT separados | SIA (PA_MVM, mês de processamento) e CNES (COMPETEN): AAAAMM | ano_mes (AAAAMM) |
| Tipo de unidade | CNES-ST: texto "02" | API CNES: inteiro 2 | texto com 2 dígitos; prioridade para o CNES-ST |
| Código CNES | SIH, SIA, CNES (às vezes sem zeros à esquerda) | – | texto com 7 dígitos |
