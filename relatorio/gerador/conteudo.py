# Conteúdo do relatório (mesmo texto do PDF entregue). Executado por extrair.py.
# ============================== 1. DESCRIÇÃO ==============================
h1("1. Descrição do Problema")
h2("1.1 Tema geral do trabalho")
p("O tema do trabalho é a <b>cobertura da atenção básica (Atenção Primária à Saúde – APS) no município de São Carlos (SP)</b>, "
  "analisada a partir de três ângulos complementares: a <b>oferta</b> de equipes de saúde, a <b>demanda</b> por atendimentos "
  "ambulatoriais e as <b>internações hospitalares evitáveis</b>. O trabalho se insere na temática da disciplina de apoio à "
  "formulação de políticas públicas municipais e utiliza exclusivamente dados reais e oficiais do Sistema Único de Saúde (SUS) "
  "e do IBGE.")
p("A atenção básica é a porta de entrada do SUS: são as Unidades Básicas de Saúde (UBS) e as Unidades de Saúde da Família (USF), "
  "com suas equipes de Saúde da Família (eSF) e de Atenção Primária (eAP), que acompanham a população de um território. "
  "Quando esse acompanhamento funciona, problemas como hipertensão, diabetes, asma ou infecções urinárias são controlados no "
  "posto de saúde. Quando falha, eles evoluem e acabam em internações hospitalares, que são mais caras para o município e piores "
  "para o paciente. Essas internações são chamadas de <b>Internações por Condições Sensíveis à Atenção Primária (ICSAP)</b> e "
  "têm uma lista oficial definida pela Portaria SAS/MS nº 221/2008. A taxa de ICSAP é um dos indicadores mais usados para "
  "avaliar a efetividade da atenção básica.")
p("A <b>importância</b> do tema para a gestão municipal está em responder perguntas concretas: quantas equipes de atenção "
  "básica o município mantém ao longo do tempo e onde elas estão; que tipo de atendimento ambulatorial a rede realiza; quais "
  "internações da população são evitáveis, em que grupos da população e por quais causas; e se variações na oferta de equipes "
  "acompanham variações nas internações evitáveis. As respostas apoiam decisões como abrir ou reforçar equipes, priorizar linhas "
  "de cuidado (por exemplo, hipertensão e diabetes em idosos) e acompanhar o efeito dessas políticas.")

h2("1.2 Fontes de dados")
p("O data warehouse é povoado por cinco fontes, todas públicas e oficiais. As três primeiras são as principais e vêm do "
  "DATASUS (Departamento de Informática do SUS), obtidas com a biblioteca PySUS; as duas últimas são fontes auxiliares usadas "
  "para enriquecer e integrar as dimensões.")
tabela(["Fonte", "Conteúdo", "Uso no DW"], [
    ["CNES – Cadastro Nacional de Estabelecimentos de Saúde, arquivos EP (equipes) e ST (estabelecimentos)",
     "Equipes de saúde cadastradas em cada estabelecimento, com tipo e datas de ativação e desativação; características dos estabelecimentos (tipo de unidade, gestão, município)",
     "Fato de equipes; dimensões de estabelecimento e tipo de equipe"],
    ["SIH-SUS – Sistema de Informações Hospitalares, arquivo RD (AIH reduzida)",
     "Uma linha por Autorização de Internação Hospitalar: paciente (sexo, idade, município de residência), hospital, diagnóstico, procedimento, dias de permanência, valor",
     "Fato de internações; dimensões de diagnóstico, procedimento, perfil do paciente, localidade e bugiganga"],
    ["SIA-SUS – Sistema de Informações Ambulatoriais, arquivo PA (produção ambulatorial)",
     "Produção ambulatorial por estabelecimento, procedimento, competência, ocupação do profissional (CBO) e perfil do paciente; quantidades e valores apresentados e aprovados",
     "Fato de produção ambulatorial; dimensões de procedimento, perfil, localidade e CBO"],
    ["IBGE – API de Localidades", "Municípios de SP com código de 7 dígitos, nome, região imediata e região intermediária",
     "Nomes e hierarquia geográfica das dimensões de localidade e estabelecimento"],
    ["Ministério da Saúde – API de Dados Abertos (CNES)", "Nome fantasia, bairro e coordenadas de cada estabelecimento",
     "Atributos descritivos da dimensão de estabelecimento"],
], [4.3, 6.8, 5.2])
p("<b>Recorte.</b> O período analisado vai de janeiro de 2023 a dezembro de 2024 (24 competências mensais). Os arquivos do "
  "DATASUS são estaduais; do estado de São Paulo são mantidos apenas os registros ligados a São Carlos: equipes sediadas no "
  "município, e internações e atendimentos de pacientes <b>residentes</b> em São Carlos ou <b>atendidos</b> em São Carlos. "
  "Manter os dois critérios permite analisar tanto a população do município (que às vezes é internada em outras cidades) "
  "quanto a rede instalada no município (que também atende moradores da região).")

h2("1.3 Processos de negócio")
p("Foram modelados três processos de negócio (assuntos de interesse), cada um dando origem a uma tabela de fatos.")

h3("Processo 1 – Oferta de equipes da atenção básica")
p("<b>Descrição e justificativa.</b> Mede a capacidade instalada da atenção básica: quantas equipes estão ativas, de que tipo e "
  "em quais estabelecimentos. É a variável de política pública mais diretamente controlada pelo gestor municipal.")
bullets([
    "<b>Grão:</b> uma equipe ativa em um estabelecimento em um mês (fotografia mensal, ou <i>snapshot</i> periódico).",
    "<b>Dimensões:</b> tempo (mês), estabelecimento, tipo de equipe. O identificador da equipe é guardado como dimensão degenerada.",
    "<b>Fatos:</b> não há medida numérica armazenada; trata-se de uma <b>tabela de fatos sem fato</b>. O número de equipes é obtido "
    "contando as linhas. Essa contagem é <b>semiaditiva</b>: pode ser somada entre estabelecimentos e tipos de equipe, mas não "
    "ao longo do tempo (somar as equipes de janeiro e de fevereiro contaria a mesma equipe duas vezes). Ao agregar vários meses, "
    "usa-se a média mensal ou o valor do último mês.",
])
h3("Processo 2 – Internações hospitalares")
p("<b>Descrição e justificativa.</b> Registra cada internação paga pelo SUS. Permite identificar as internações sensíveis à "
  "atenção primária, que funcionam como sinal de falha da rede básica, e caracterizá-las por causa, faixa etária, sexo e hospital.")
bullets([
    "<b>Grão:</b> uma internação (uma AIH).",
    "<b>Dimensões:</b> tempo, estabelecimento (hospital), procedimento realizado, diagnóstico principal, perfil do paciente, "
    "localidade de residência do paciente e tabela bugiganga (caráter do atendimento, óbito, uso de UTI). O número da AIH é "
    "dimensão degenerada.",
    "<b>Fatos:</b> quantidade de internações (sempre 1 por linha, <b>aditivo</b>), dias de permanência (<b>aditivo</b>) e valor "
    "total pago em reais (<b>aditivo</b>). A média de permanência é um fato <b>derivado e não aditivo</b>, obtido pela soma dos "
    "dias dividida pela quantidade de internações.",
])
h3("Processo 3 – Produção ambulatorial")
p("<b>Descrição e justificativa.</b> Mede a demanda atendida nos ambulatórios do SUS: consultas, exames, procedimentos e ações "
  "de prevenção. Mostra o volume e o tipo de atendimento que a rede realiza e o perfil de quem é atendido.")
bullets([
    "<b>Grão:</b> estabelecimento × procedimento × mês × perfil do paciente (sexo e faixa etária) × município de residência × "
    "ocupação do profissional. É o menor nível de detalhe disponível no arquivo público do SIA, que já vem parcialmente agregado.",
    "<b>Dimensões:</b> tempo, estabelecimento, procedimento, perfil do paciente, localidade de residência, ocupação (CBO).",
    "<b>Fatos:</b> quantidade apresentada, quantidade aprovada, valor apresentado e valor aprovado, todos <b>aditivos</b>. A taxa de "
    "aprovação é um fato <b>derivado e não aditivo</b>: quantidade aprovada dividida pela quantidade apresentada, calculada "
    "sempre sobre as somas e nunca somando taxas.",
])

h3("Medidas derivadas entre processos")
bullets([
    "<b>Cobertura estimada de Saúde da Família (%)</b> = número de equipes eSF × 3.450 pessoas ÷ população do município × 100, "
    "limitada a 100%. O parâmetro de 3.450 pessoas por equipe é o usado historicamente pelo Ministério da Saúde. Não aditiva.",
    "<b>Taxa de ICSAP por 10 mil habitantes</b> = internações ICSAP de residentes ÷ população × 10.000. Não aditiva.",
    "A população usada é a do Censo 2022 do IBGE para São Carlos (254.857 habitantes).",
])

h2("1.4 Dimensões e seus atributos")
p("Todas as dimensões usam uma <b>chave artificial</b> (<i>surrogate key</i>, prefixo <font name='Mono'>sk_</font>) como chave "
  "primária, independente dos códigos das fontes. Cada dimensão também tem um membro de chave 0, “Não informado”, que recebe os "
  "fatos cujo código não é encontrado, para que nenhum registro seja perdido na carga. Nas tabelas abaixo, a coluna "
  "“Relação” indica se o atributo participa de uma hierarquia ou é apenas descritivo.")

DIMS = [
 ("dim_tempo", "Mês de competência, isto é, o mês a que o registro se refere no sistema do Ministério da Saúde. Todas as fontes são mensais, então o mês é o menor nível de detalhe comum.", [
  ["sk_tempo", "Chave artificial", "–", "Gerada na carga"],
  ["ano_mes", "Competência no formato AAAAMM", "Hierarquia (nível mais baixo)", "SIH: ANO_CMPT + MES_CMPT; SIA: PA_MVM; CNES: COMPETEN (integração)"],
  ["mes", "Número do mês (1 a 12)", "Descritivo", "Derivado de ano_mes"],
  ["nome_mes", "Nome abreviado do mês", "Descritivo", "Derivado de ano_mes"],
  ["trimestre", "Trimestre do ano (ex.: 2024-T1)", "Hierarquia", "Derivado de ano_mes"],
  ["semestre", "Semestre do ano (ex.: 2024-S1)", "Hierarquia", "Derivado de ano_mes"],
  ["ano", "Ano", "Hierarquia (nível mais alto)", "Derivado de ano_mes"]]),
 ("dim_estabelecimento", "Estabelecimento de saúde (UBS, USF, hospital, clínica, pronto atendimento etc.), identificado pelo código CNES. É compartilhada pelos três processos.", [
  ["sk_estabelecimento", "Chave artificial", "–", "Gerada na carga"],
  ["cnes", "Código nacional do estabelecimento, 7 dígitos (chave natural)", "Hierarquia (nível mais baixo)", "CNES, SIH (CNES) e SIA (PA_CODUNI), padronizado com zeros à esquerda"],
  ["nome", "Nome fantasia", "Descritivo", "API de Dados Abertos (nome_fantasia)"],
  ["tipo_unidade_cod / tipo_unidade", "Tipo do estabelecimento (ex.: 02 – Centro de saúde / Unidade básica)", "Hierarquia", "CNES-ST (TP_UNID); na falta, API (codigo_tipo_unidade)"],
  ["nivel_atencao", "Atenção Primária, Especializada, Hospitalar, Urgência ou Outros", "Hierarquia", "Derivado do tipo de unidade"],
  ["gestao", "Gestão municipal, estadual ou dupla", "Descritivo", "CNES-ST (TPGESTAO)"],
  ["bairro", "Bairro do estabelecimento", "Hierarquia", "API de Dados Abertos"],
  ["latitude / longitude", "Coordenadas geográficas", "Descritivos", "API de Dados Abertos"],
  ["cod_municipio / municipio", "Município do estabelecimento", "Hierarquia", "CNES-ST (CODUFMUN) + nome do IBGE"],
  ["regiao_imediata", "Região geográfica imediata do IBGE", "Hierarquia", "IBGE"],
  ["uf", "Unidade da federação", "Hierarquia (nível mais alto)", "IBGE / prefixo do código do município"]]),
 ("dim_localidade", "Município de residência do paciente. Permite separar a população de São Carlos dos pacientes de outras cidades atendidos no município.", [
  ["sk_localidade", "Chave artificial", "–", "Gerada na carga"],
  ["cod_municipio", "Código do município, 6 dígitos", "Hierarquia (nível mais baixo)", "SIH (MUNIC_RES), SIA (PA_MUNPCN), IBGE (7 dígitos convertidos)"],
  ["municipio", "Nome do município", "Descritivo do nível município", "IBGE"],
  ["regiao_imediata", "Região imediata do IBGE (ex.: São Carlos)", "Hierarquia", "IBGE"],
  ["regiao_intermediaria", "Região intermediária do IBGE (ex.: Araraquara)", "Hierarquia", "IBGE"],
  ["uf", "Unidade da federação", "Hierarquia (nível mais alto)", "IBGE / prefixo do código"]]),
 ("dim_tipo_equipe", "Tipo da equipe de saúde, conforme a classificação do CNES.", [
  ["sk_tipo_equipe", "Chave artificial", "–", "Gerada na carga"],
  ["tipo_equipe_cod", "Código do tipo (ex.: 70)", "Hierarquia (nível mais baixo)", "CNES-EP (TIPO_EQP)"],
  ["tipo_equipe", "Descrição (ex.: eSF – Equipe de Saúde da Família)", "Descritivo do código", "Tabela de tipos de equipe do CNES"],
  ["categoria_equipe", "Saúde da Família, Atenção Primária, Saúde Bucal, Multiprofissional ou Outras", "Hierarquia (nível mais alto)", "Classificação definida pelo grupo"]]),
 ("dim_procedimento", "Procedimento da Tabela de Procedimentos do SUS (SIGTAP), usada tanto pelo SIA quanto pelo SIH. O próprio código de 10 dígitos é hierárquico.", [
  ["sk_procedimento", "Chave artificial", "–", "Gerada na carga"],
  ["cod_procedimento", "Código de 10 dígitos", "Hierarquia (nível mais baixo)", "SIA (PA_PROC_ID), SIH (PROC_REA)"],
  ["forma_organizacao_cod", "6 primeiros dígitos", "Hierarquia", "Derivado do código"],
  ["subgrupo_cod", "4 primeiros dígitos", "Hierarquia", "Derivado do código"],
  ["grupo_cod / grupo", "2 primeiros dígitos e nome do grupo (ex.: 03 – Procedimentos clínicos)", "Hierarquia (nível mais alto)", "Derivado do código + SIGTAP"]]),
 ("dim_diagnostico", "Diagnóstico principal da internação segundo a CID-10, com a classificação de condição sensível à atenção primária.", [
  ["sk_diagnostico", "Chave artificial", "–", "Gerada na carga"],
  ["cid", "Código CID-10 com 4 caracteres (ex.: J181)", "Hierarquia (nível mais baixo)", "SIH (DIAG_PRINC)"],
  ["cid_categoria", "3 primeiros caracteres (ex.: J18)", "Hierarquia", "Derivado do código"],
  ["capitulo_num / capitulo", "Capítulo da CID-10 (ex.: X – Aparelho respiratório)", "Hierarquia", "Tabela da CID-10"],
  ["grupo_icsap", "Um dos 19 grupos de ICSAP ou “Não ICSAP”", "Hierarquia", "Portaria SAS/MS nº 221/2008"],
  ["icsap", "Sim / Não", "Hierarquia (nível mais alto)", "Derivado de grupo_icsap"]]),
 ("dim_perfil_paciente", "Perfil demográfico do paciente. É uma mini-dimensão com todas as combinações de sexo e faixa etária, compartilhada pelos processos 2 e 3.", [
  ["sk_perfil", "Chave artificial", "–", "Gerada na carga"],
  ["sexo", "M, F ou I (ignorado)", "Descritivo (independente da faixa)", "SIH (SEXO) e SIA (PA_SEXO), com integração"],
  ["sexo_desc", "Masculino, Feminino ou Ignorado", "Descritivo", "Derivado de sexo"],
  ["faixa_etaria", "00-04, 05-09, 10-14, 15-19, 20-39, 40-59, 60-69, 70-79, 80+ ou Ignorada", "Hierarquia (nível mais baixo)", "SIH (IDADE + COD_IDADE) e SIA (PA_IDADE), com integração"],
  ["ciclo_vida", "Criança, Adolescente, Adulto ou Idoso", "Hierarquia (nível mais alto)", "Derivado da faixa etária"]]),
 ("dim_cbo", "Ocupação do profissional que realizou o atendimento ambulatorial, segundo a Classificação Brasileira de Ocupações.", [
  ["sk_cbo", "Chave artificial", "–", "Gerada na carga"],
  ["cbo", "Código de 6 dígitos (ex.: 225142 – médico da estratégia de Saúde da Família)", "Hierarquia (nível mais baixo)", "SIA (PA_CBOCOD)"],
  ["familia_cbo", "4 primeiros dígitos", "Hierarquia", "Derivado do código"],
  ["categoria_profissional", "Médico, Enfermeiro, Técnico/auxiliar de enfermagem, Cirurgião-dentista, Agente comunitário ou Outros", "Hierarquia (nível mais alto)", "Classificação definida pelo grupo a partir da família"]]),
 ("dim_junk_internacao", "Tabela bugiganga (<i>junk dimension</i>) que reúne indicadores de baixa cardinalidade da internação. Isolados, cada um viraria uma dimensão com dois a seis valores; juntos, formam uma única dimensão com apenas as combinações que ocorrem nos dados.", [
  ["sk_junk", "Chave artificial", "–", "Gerada na carga"],
  ["carater_atendimento", "Eletivo, Urgência ou tipos de acidente", "Descritivo", "SIH (CAR_INT)"],
  ["obito", "Sim / Não", "Descritivo", "SIH (MORTE)"],
  ["uti", "Sim / Não (houve diárias de UTI)", "Descritivo", "SIH (UTI_MES_TO &gt; 0)"]]),
]
for nome, desc, linhas in DIMS:
    h3(nome)
    p(desc)
    tabela(["Atributo", "Significado", "Relação", "Povoamento (fonte)"], linhas, [3.6, 5.0, 3.2, 4.5])

h2("1.5 Povoamento e integração dos dados")
p("O povoamento segue um processo de extração, transformação e carga. Cada arquivo mensal do estado de São Paulo é lido em "
  "lotes, apenas com as colunas necessárias, e só os registros ligados a São Carlos são mantidos. Em seguida, os códigos são "
  "padronizados, as dimensões são montadas com chaves artificiais e as tabelas de fatos recebem essas chaves.")
p("A <b>integração</b> é necessária sempre que o mesmo dado chega de mais de uma fonte com representações diferentes. "
  "Os casos encontrados e a representação escolhida para o data warehouse são:")
tabela(["Dado", "Fonte A", "Fonte B", "Representação no DW"], [
    ["Sexo", "SIH: 1 = masculino; 3 (ou 2) = feminino; demais = ignorado", "SIA: M, F; demais = ignorado", "M, F, I"],
    ["Idade", "SIH: valor + unidade (COD_IDADE: dias, meses, anos ou centenas de anos)", "SIA: idade em anos", "Idade em anos convertida para faixa etária; menores de 1 ano entram em 00-04"],
    ["Município", "DATASUS: código de 6 dígitos", "IBGE: código de 7 dígitos (com dígito verificador)", "6 dígitos, com o nome vindo do IBGE"],
    ["Competência", "SIH: ano e mês em colunas separadas", "SIA e CNES: AAAAMM", "ano_mes no formato AAAAMM"],
    ["Tipo de unidade", "CNES-ST: texto com dois dígitos (\"02\")", "API de Dados Abertos: inteiro (2)", "Texto com dois dígitos; o CNES-ST tem prioridade e a API completa o que faltar"],
    ["Código CNES", "SIH, SIA e CNES, às vezes sem zeros à esquerda", "API: inteiro", "Texto com 7 dígitos"],
    ["Município do estabelecimento", "CNES-ST (CODUFMUN)", "API de Dados Abertos (codigo_municipio)", "CNES-ST com prioridade; API como alternativa"],
], [2.8, 4.4, 4.4, 4.7])

p("O processo foi executado com os dados reais de janeiro de 2023 a dezembro de 2024 (notebook "
  "<font name='Mono'>dw_aps_sao_carlos.ipynb</font>, banco DuckDB). A carga resultou em 1.686 linhas em fato_equipe, 39.609 em "
  "fato_internacao e 193.723 em fato_producao_ambulatorial, com todas as chaves estrangeiras resolvidas. Para validar a extração, "
  "o número de AIHs de residentes foi comparado com o TabNet do DATASUS: em janeiro de 2024 o TabNet mostra 1.287 e o DW 1.285, "
  "diferença que corresponde exatamente às AIHs de continuação descartadas de propósito; em abril de 2023 e dezembro de 2024 a "
  "diferença é de uma AIH em cerca de 1.400.")

h2("1.6 Particularidades do problema")
bullets([
    "<b>Competência versus data do evento.</b> Os sistemas do SUS organizam os dados pelo mês de apresentação (competência). "
    "Uma internação iniciada em dezembro pode ser apresentada em janeiro. O DW usa a competência em todos os processos, o que "
    "mantém os três fatos comparáveis e coincide com a forma como o próprio Ministério da Saúde tabula os dados. No SIA isso significa usar o mês de processamento (<font name='Mono'>PA_MVM</font>), e não o mês do atendimento (<font name='Mono'>PA_CMP</font>): produção apresentada com atraso cairia em meses fora do período carregado.",
    "<b>AIH de longa permanência.</b> Internações muito longas geram AIHs de continuação (identificação tipo 5) em meses seguintes. "
    "Essas linhas são descartadas para que cada internação seja contada uma única vez.",
    "<b>Equipes ativas.</b> O arquivo de equipes do CNES pode listar equipes já desativadas. Só entram no fato as equipes sem data "
    "de desativação ou com desativação posterior ao mês. O campo <font name='Mono'>DT_DESAT</font> vem como AAAAMM, "
    "e o valor 900001 indica equipe nunca desativada.",
    "<b>Residência versus local de atendimento.</b> A pergunta de política pública é sobre a população de São Carlos, por isso as "
    "consultas de demanda filtram pelo município de residência. As consultas sobre a rede instalada filtram pelo município do "
    "estabelecimento.",
    "<b>Limitação do SIA para a atenção básica.</b> Desde a implantação do e-SUS APS, a produção das UBS é registrada no SISAB e "
    "não no SIA. Os dados reais confirmaram isso de forma extrema: as unidades de atenção primária de São Carlos não têm nenhum "
    "procedimento no SIA em 2023 e 2024. A produção ambulatorial do SIA representa, portanto, a atenção especializada, "
    "diagnóstica e de urgência.",
    "<b>Cobertura estimada.</b> O indicador de cobertura calculado no DW é uma aproximação baseada no parâmetro de pessoas por "
    "equipe; a metodologia oficial de cobertura do Ministério mudou ao longo dos anos.",
])

# ============================== 2. ESQUEMAS ==============================
S.append(PageBreak())
h1("2. Esquemas")
p("Legenda dos diagramas: <b>PK</b> – chave primária artificial; <b>FK</b> – chave estrangeira para uma dimensão; "
  "<b>DD</b> – dimensão degenerada; <b>M</b> – medida. As hierarquias usam o operador de ordenação parcial ≤: "
  "<font name='Mono'>A ≤ B</font> significa que A é um nível mais detalhado que B, e cada valor de A pertence a um único valor de B.")

def estrela(tit, img, leg, hierarquias, agreg):
    figura(IMG + img, leg, max_h=19.5, titulo=tit)
    h3("Hierarquias das dimensões")
    for d, hs in hierarquias:
        S.append({"k": "pbold", "r": runs(d)})
        hier(*hs)
    h3("Funções de agregação")
    tabela(["Fato", "Tipo", "Função de agregação"], agreg, [4.6, 3.6, 8.1], keep=True)

H_TEMPO = ("dim_tempo", ["ano_mes ≤ trimestre ≤ semestre ≤ ano"])
H_EST = ("dim_estabelecimento", ["cnes ≤ tipo_unidade ≤ nivel_atencao", "cnes ≤ bairro ≤ municipio ≤ regiao_imediata ≤ uf"])
H_LOC = ("dim_localidade", ["municipio ≤ regiao_imediata ≤ regiao_intermediaria ≤ uf"])
H_PROC = ("dim_procedimento", ["cod_procedimento ≤ forma_organizacao_cod ≤ subgrupo_cod ≤ grupo_cod"])
H_PERF = ("dim_perfil_paciente", ["faixa_etaria ≤ ciclo_vida", "(sexo é descritivo, sem hierarquia)"])

estrela("2.1 Esquema estrela 1 – Oferta de equipes (fato sem fato)", "estrela_1_equipe.png",
        "Figura 1 – Esquema estrela da oferta de equipes da atenção básica.",
        [H_TEMPO, H_EST, ("dim_tipo_equipe", ["tipo_equipe_cod ≤ categoria_equipe"])],
        [["número de equipes (contagem de linhas)", "Semiaditivo", "CONTAGEM no mesmo mês; entre meses, MÉDIA das contagens mensais ou valor do ÚLTIMO mês"]])

estrela("2.2 Esquema estrela 2 – Internações hospitalares", "estrela_2_internacao.png",
        "Figura 2 – Esquema estrela das internações hospitalares.",
        [H_TEMPO, H_EST, H_PROC,
         ("dim_diagnostico", ["cid ≤ cid_categoria ≤ capitulo", "cid ≤ grupo_icsap ≤ icsap"]),
         H_PERF, H_LOC, ("dim_junk_internacao", ["(sem hierarquia; atributos descritivos)"])],
        [["qtd_internacoes", "Aditivo", "SOMA"], ["dias_permanencia", "Aditivo", "SOMA"],
         ["valor_total", "Aditivo", "SOMA"],
         ["média de permanência (derivado)", "Não aditivo", "SOMA(dias_permanencia) ÷ SOMA(qtd_internacoes)"],
         ["taxa de ICSAP (derivado)", "Não aditivo", "SOMA(qtd_internacoes ICSAP) ÷ população × 10.000"]])

estrela("2.3 Esquema estrela 3 – Produção ambulatorial", "estrela_3_producao.png",
        "Figura 3 – Esquema estrela da produção ambulatorial.",
        [H_TEMPO, H_EST, H_PROC, H_PERF, H_LOC,
         ("dim_cbo", ["cbo ≤ familia_cbo ≤ categoria_profissional"])],
        [["qtd_apresentada", "Aditivo", "SOMA"], ["qtd_aprovada", "Aditivo", "SOMA"],
         ["valor_apresentado", "Aditivo", "SOMA"], ["valor_aprovado", "Aditivo", "SOMA"],
         ["taxa de aprovação (derivado)", "Não aditivo", "SOMA(qtd_aprovada) ÷ SOMA(qtd_apresentada)"]])

h2("2.4 Aspectos adicionais de modelagem")
bullets([
    "<b>Chaves artificiais:</b> todas as dimensões têm chave primária artificial, o que isola o DW de mudanças nos códigos das "
    "fontes, permite o membro “Não informado” (chave 0) e reduz o tamanho das tabelas de fatos.",
    "<b>Tabela bugiganga:</b> <font name='Mono'>dim_junk_internacao</font> reúne caráter do atendimento, óbito e uso de UTI.",
    "<b>Dimensões degeneradas:</b> <font name='Mono'>n_aih</font> em fato_internacao e <font name='Mono'>id_equipe</font> em "
    "fato_equipe. São identificadores sem outros atributos, úteis para contar itens distintos e rastrear o registro na fonte.",
    "<b>Tabela de fatos sem fato:</b> <font name='Mono'>fato_equipe</font> registra apenas a existência de uma equipe ativa em um "
    "estabelecimento em um mês; a análise é feita por contagem.",
    "<b>Mini-dimensão:</b> <font name='Mono'>dim_perfil_paciente</font> separa os atributos demográficos do paciente, que no SUS não "
    "tem identificação pública, em uma dimensão pequena e compartilhada.",
])

S.append(PageBreak())
figura(ROT, "Figura 4 – Constelação de fatos (imagem girada). Dimensões compartilhadas com borda grossa.",
       max_h=20.5, titulo="2.5 Constelação de fatos")
h3("Processo de projeto da constelação")
p("A constelação foi obtida em quatro passos:")
bullets([
    "<b>1. Modelagem independente.</b> Cada processo de negócio foi modelado como uma estrela própria, com seu grão, suas "
    "dimensões e seus fatos (Figuras 1 a 3).",
    "<b>2. Identificação das dimensões em comum.</b> Comparando as estrelas, identificaram-se as dimensões que aparecem em mais de "
    "uma: tempo, estabelecimento, procedimento, perfil do paciente e localidade.",
    "<b>3. Conformação das dimensões.</b> Cada dimensão comum passou a ter uma única definição, com a mesma chave, os mesmos "
    "atributos e os mesmos valores em todas as estrelas. Por exemplo, o tempo usa sempre o mês de competência, o sexo usa sempre "
    "M/F/I e o estabelecimento usa sempre o CNES com 7 dígitos, qualquer que seja a fonte. Foi para isso que o grão do tempo foi "
    "fixado no mês, o menor nível comum às três fontes.",
    "<b>4. Junção.</b> As três tabelas de fatos passam a apontar para as mesmas tabelas de dimensão, formando a constelação. "
    "Isso permite comparar os três processos na mesma análise por meio da operação drill-across (Consulta 5).",
])
p("A matriz abaixo resume quais dimensões são usadas por cada tabela de fatos.")
M = "✓"
tabela(["Dimensão", "fato_equipe", "fato_internacao", "fato_producao_ambulatorial"], [
    ["dim_tempo", M, M, M], ["dim_estabelecimento", M, M, M], ["dim_procedimento", "", M, M],
    ["dim_perfil_paciente", "", M, M], ["dim_localidade", "", M, M], ["dim_tipo_equipe", M, "", ""],
    ["dim_diagnostico", "", M, ""], ["dim_junk_internacao", "", M, ""], ["dim_cbo", "", "", M]],
    [5.0, 3.3, 3.5, 4.5], keep=True)

# ============================== 3. CONSULTAS ==============================
S.append(PageBreak())
h1("3. Consultas")
p("As consultas abaixo são as principais perguntas que o data warehouse deve responder. Todas usam como filtro o município de "
  "São Carlos, pela residência do paciente (demanda) ou pela localização do estabelecimento (oferta).")
p("Todas foram executadas no DW povoado com os dados reais de 2023 e 2024. Para cada uma, o relatório mostra o resultado obtido e "
  "uma captura da célula do notebook com o código SQL e a saída. Tabelas longas aparecem com início e fim, separados por “…”.")

CONS = [
 ("Consulta 1 – Roll-up", "Roll-up na dimensão tempo (ano_mes → trimestre → ano).",
  "Qual o número de internações por condições sensíveis à atenção primária de residentes em São Carlos em cada mês? Em seguida, "
  "agregar o resultado por trimestre e por ano.",
  "Tabela de fatos: fato_internacao. Dimensões: tempo (ano_mes, trimestre, ano), diagnóstico (icsap = Sim), localidade "
  "(município de residência = São Carlos). Medida: SOMA de qtd_internacoes.",
  "É o indicador central de efetividade da atenção básica. A visão mensal mostra sazonalidade (por exemplo, doenças "
  "respiratórias no inverno) e a visão anual mostra a tendência que interessa ao planejamento plurianual do município."),
 ("Consulta 2 – Drill-down", "Drill-down na dimensão procedimento (grupo → subgrupo → procedimento).",
  "Qual a quantidade aprovada de procedimentos ambulatoriais realizados em estabelecimentos de São Carlos por grupo de "
  "procedimento? Para o grupo com maior volume, detalhar por subgrupo e, para o subgrupo principal, por procedimento.",
  "Tabela de fatos: fato_producao_ambulatorial. Dimensões: procedimento (grupo_cod, subgrupo_cod, cod_procedimento), "
  "estabelecimento (município = São Carlos). Medidas: SOMA de qtd_aprovada e de valor_aprovado.",
  "Mostra que tipo de atendimento a rede ambulatorial mais realiza e permite descer até os procedimentos específicos que "
  "concentram o volume e o gasto, apoiando o dimensionamento de oferta e de contratos."),
 ("Consulta 3 – Slice and dice", "Slice na dimensão tempo (ano = 2024) e dice nas dimensões perfil do paciente (ciclo de vida = "
  "Idoso) e diagnóstico (icsap = Sim).",
  "Quantas internações por condições sensíveis à atenção primária de idosos residentes em São Carlos ocorreram em 2024, e qual "
  "a média de dias de permanência, por grupo de causa e por sexo?",
  "Tabela de fatos: fato_internacao. Dimensões: tempo (ano), perfil do paciente (ciclo_vida, sexo), diagnóstico (icsap, "
  "grupo_icsap), localidade. Medidas: SOMA de qtd_internacoes; média de permanência (derivada).",
  "Os idosos concentram as condições crônicas acompanhadas pela atenção básica, como doenças cerebrovasculares e insuficiência cardíaca. Identificar "
  "as causas que mais internam esse grupo orienta ações como grupos de hipertensos e diabéticos e visitas domiciliares."),
 ("Consulta 4 – Pivot", "Pivot (rotação) entre as dimensões diagnóstico e perfil do paciente.",
  "Qual o número de internações por condições sensíveis à atenção primária de residentes em São Carlos por grupo de causa "
  "(linhas) e ciclo de vida (colunas)? Em seguida, rotacionar a visão, com ciclo de vida nas linhas e grupo de causa nas colunas.",
  "Tabela de fatos: fato_internacao. Dimensões: diagnóstico (grupo_icsap), perfil do paciente (ciclo_vida), localidade. "
  "Medida: SOMA de qtd_internacoes.",
  "As duas orientações respondem perguntas diferentes do gestor: “quais causas pesam em cada fase da vida?” (útil para "
  "programas por público, como saúde da criança e do idoso) e “qual fase da vida mais sofre com cada causa?” (útil para linhas "
  "de cuidado por doença)."),
 ("Consulta 5 – Drill-across", "Drill-across entre fato_equipe, fato_producao_ambulatorial e fato_internacao, pela dimensão "
  "conforme tempo (e pelo município).",
  "Em cada mês, quantas equipes de Saúde da Família estavam ativas em São Carlos, qual a cobertura estimada correspondente, "
  "quantos procedimentos ambulatoriais foram aprovados nos estabelecimentos de atenção primária do município e quantas "
  "internações por condições sensíveis à atenção primária de residentes ocorreram (em número absoluto e por 10 mil habitantes)?",
  "Cada tabela de fatos é agregada separadamente por ano_mes e os três resultados são combinados pelo mês. fato_equipe: "
  "CONTAGEM de equipes com categoria_equipe = Saúde da Família. fato_producao_ambulatorial: SOMA de qtd_aprovada com "
  "nivel_atencao = Atenção Primária. fato_internacao: SOMA de qtd_internacoes com icsap = Sim e residência = São Carlos. "
  "Medidas derivadas: cobertura estimada e taxa de ICSAP.",
  "Responde a pergunta central do trabalho: variações na oferta de atenção básica acompanham variações nas internações "
  "evitáveis? Só é possível porque as três estrelas compartilham dimensões conformes, e o resultado subsidia a decisão de "
  "expandir ou manter equipes."),
]
RESULTADOS = [
 ("Foram 5.255 internações por condições sensíveis à atenção primária de residentes nos dois anos, 16% das 32.799 internações "
  "de residentes. No nível mês, o maior valor é dezembro de 2023 (291) e o menor, janeiro de 2024 (167); como o mês é o de "
  "processamento da AIH, parte dessa oscilação reflete o ritmo de apresentação dos hospitais. Subindo para trimestre, a série "
  "fica entre 572 e 728, e no ano passa de 2.700 (2023) para 2.555 (2024), queda de cerca de 5%.",
  [("consulta1.png", "Consulta 1 no notebook: ICSAP por mês e roll-up para trimestre e ano (linhas com NULL são os subtotais).", 20.5)]),
 ("O grupo 02 (procedimentos com finalidade diagnóstica) lidera em quantidade, com 1,77 milhão de procedimentos aprovados; o "
  "grupo 03 (procedimentos clínicos) vem em segundo em quantidade, mas tem o maior valor aprovado, cerca de R$ 31,3 milhões. "
  "Descendo no grupo 02, o subgrupo 0202 (diagnóstico em laboratório clínico) concentra 1,39 milhão, e no nível de procedimento "
  "os maiores volumes são o hemograma completo (0202020380, 126.646) e a dosagem de creatinina (0202010317, 101.989).",
  [("consulta2.png", "Consulta 2 no notebook: produção aprovada por grupo e drill-down até o procedimento.", 21.5)]),
 ("Foram 1.358 internações evitáveis de idosos residentes em 2024. As doenças cerebrovasculares lideram (170 homens e 154 "
  "mulheres), seguidas da insuficiência cardíaca (128 mulheres e 114 homens) e da angina (89 homens). Entre as causas mais "
  "frequentes, as doenças pulmonares e a insuficiência cardíaca têm as maiores médias de permanência.",
  [("consulta3.png", "Consulta 3 no notebook: ICSAP de idosos residentes em 2024 por grupo de causa e sexo.", 12.5)]),
 ("Na primeira orientação, cada causa mostra em que fase da vida pesa: as doenças circulatórias são quase exclusivas de adultos "
  "e idosos (621 idosos com doença cerebrovascular nos dois anos). Na orientação rotacionada, cada fase da vida mostra suas "
  "causas: nas crianças predominam as doenças pulmonares (329) e as gastroenterites (79); nos adultos, as doenças "
  "cerebrovasculares (229), a infecção do rim e trato urinário (204) e a de pele e subcutâneo (189).",
  [("consulta4.png", "Consulta 4 no notebook: ICSAP por causa × ciclo de vida e a mesma tabela rotacionada.", 15)]),
 ("O drill-across funcionou como projetado e expôs dois fatos sobre as fontes. Primeiro, São Carlos manteve 23 equipes de Saúde "
  "da Família ativas em todos os 24 meses, o que dá cobertura estimada constante de 31,1%. Segundo, a produção APS no SIA é zero "
  "em todos os meses, porque a produção das UBS vai para o SISAB (Seção 1.6). A taxa de ICSAP variou entre 6,55 e 11,42 por "
  "10 mil habitantes, terminando 2024 em 8,40. Com a oferta constante no período, ainda não é possível relacionar variações de "
  "cobertura e de internações evitáveis: isso exige uma série mais longa e a inclusão do SISAB como fonte.",
  [("consulta5.png", "Consulta 5 no notebook: as três tabelas de fatos agregadas por mês e combinadas por ano_mes.", 20.5),
   ("consulta5_grafico.png", "Consulta 5: resultado mês a mês, um painel por tabela de fatos com o mesmo eixo de tempo.", 12)]),
]
n_fig = 5
for (tit, op, perg, estr, just), (res, figs) in zip(CONS, RESULTADOS):
    h2(tit)
    p(f"<b>Operação OLAP:</b> {op}")
    p(f"<b>Consulta:</b> {perg}")
    p(f"<b>Elementos do esquema:</b> {estr}")
    p(f"<b>Importância e justificativa:</b> {just}")
    p(f"<b>Resultado com os dados reais:</b> {res}")
    for arq, leg, h in figs:
        figura("consultas/" + arq, f"Figura {n_fig} – {leg}", max_h=h)
        n_fig += 1

h2("Resumo das consultas")
tabela(["Consulta", "Operação", "Tabela(s) de fatos"], [
    ["1", "Roll-up", "fato_internacao"], ["2", "Drill-down", "fato_producao_ambulatorial"],
    ["3", "Slice and dice", "fato_internacao"], ["4", "Pivot", "fato_internacao"],
    ["5", "Drill-across", "fato_equipe, fato_producao_ambulatorial, fato_internacao"]], [2.5, 4, 9.8], keep=True)
