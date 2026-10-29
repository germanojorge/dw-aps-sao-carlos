# Trabalho Prático – SCC0245: Data Warehouse da Atenção Básica em São Carlos

Contexto para o Claude Code. O projeto veio do claude.ai (projeto "Trabalho de Dados"); este arquivo resume o que foi decidido e feito lá.
Situação registrada em **28/10/2026**. Atualize a seção "Situação atual" quando algo mudar.

## Quem e o quê

- Germano (NLP/IA, mestre pelo ICMC-USP) faz este trabalho em grupo. Fala português do Brasil; responda em pt-BR.
- Disciplina: **SCC0245 – Processamento Analítico de Dados**, ICMC-USP, Profa. Cristina Dutra de Aguiar.
- Temática do oferecimento: *Projetos Temáticos: Política Pública Municipal*. Usar dados públicos **reais** e oficiais (dados sintéticos só como complemento), de preferência de São Carlos, para apoiar a formulação de políticas municipais.
- Tema do grupo: **cobertura da atenção básica em São Carlos** (unidades e equipes de saúde, demanda por serviços).
- **Trabalho Prático 1** = modelagem de um data warehouse: processos de negócio, esquemas estrela, constelação de fatos e 5 consultas OLAP. Entrega em PDF + apresentação com tempo igual por integrante. O enunciado completo está em `enunciado/scc0245projeto1.pdf`.
- Preferência do grupo: **"fazer o básico bem feito, sem complicação"**. Não inflar o escopo.
- Provavelmente haverá uma parte 2 com a implementação do DW. Por isso, não modelar nada que as fontes não entreguem.

## Exigências do enunciado (resumo)

- Pelo menos 3 processos de negócio, 2 esquemas estrela, 1 constelação, 2 fontes de dados e 5 consultas (roll-up, drill-down, slice and dice, pivot, drill-across).
- O PDF segue a estrutura: Capa (instituição, curso, disciplina, docente, título, integrantes com nº USP, data), Índice, Descrição do Problema, Esquemas, Consultas.
- **Quem não estiver na capa leva nota zero.**
- Os esquemas devem usar a notação vista em aula. `enunciado/SCC0245012022OLAPexemplosAplicacao.pdf` tem exemplos de aula (formato Foco / Perspectivas / Demanda).

## Modelo do DW (como está no relatório e no notebook)

Três fatos, ligados pelas dimensões conformes tempo, estabelecimento, procedimento, perfil do paciente e localidade:

| Fato | Fonte | Grão | Medidas |
|---|---|---|---|
| `fato_equipe` (fato sem fato, snapshot periódico) | CNES-EP | equipe ativa × estabelecimento × mês | COUNT, semiaditivo no tempo; `id_equipe` = dimensão degenerada |
| `fato_internacao` | SIH-RD | uma AIH | qtd_internacoes, dias_permanencia, valor_total (aditivos); `n_aih` = dimensão degenerada |
| `fato_producao_ambulatorial` | SIA-PA | estab × proced × mês × perfil × residência × CBO | qtd/valor apresentados e aprovados (aditivos); taxa de aprovação é derivada e não aditiva |

Dimensões: `dim_tempo`, `dim_estabelecimento`, `dim_localidade`, `dim_tipo_equipe`, `dim_procedimento` (SIGTAP), `dim_diagnostico` (CID-10 + flag ICSAP), `dim_perfil_paciente` (mini-dimensão sexo × faixa etária), `dim_cbo`, `dim_junk_internacao` (tabela bugiganga: caráter, óbito, UTI). Todas usam chave artificial `sk_*` e têm um membro 0 = "Não informado".
O detalhe de cada atributo e hierarquia está em `esquemas/especificacao_esquemas.md`.

Consultas OLAP:
1. Roll-up: ICSAP de residentes por mês → trimestre → ano.
2. Drill-down: produção ambulatorial por grupo → subgrupo → procedimento.
3. Slice and dice: ICSAP de idosos em 2024 por causa e sexo.
4. Pivot: ICSAP causa × ciclo de vida, e a mesma visão rotacionada.
5. Drill-across: equipes eSF (cobertura estimada = equipes × 3.450 / população) × produção APS × taxa de ICSAP por 10 mil habitantes, mês a mês. É a pergunta central do trabalho.

Fontes auxiliares: API de localidades do IBGE (nomes e regiões dos municípios) e API de Dados Abertos do Ministério da Saúde (`apidadosabertos.saude.gov.br/cnes/estabelecimentos/{cnes}`: nome, bairro e coordenadas).

## Dados: o que já se sabe

- Download pelo **PySUS 2.x** (`pysus.cnes/sih/sia(state="SP", year=, month=, group=)`; devolve caminhos de parquet). Se o catálogo falhar, usar `source="origin", origin="FTP"`. Os arquivos são **estaduais e mensais**, e o notebook filtra São Carlos lendo em lotes.
- São Carlos: código IBGE **354890** (6 dígitos, padrão DATASUS) ou 3548906 (7 dígitos). População (Censo 2022): **254.857**, confirmada na API do IBGE (agregado 9514) em 28/10/2026.
- A API de Dados Abertos do CNES lista 36 estabelecimentos tipo 02 em São Carlos (out/2026), mas várias coordenadas coincidem: a geolocalização da API é imprecisa.
- Integrações já tratadas: sexo (SIH 1/3 contra SIA M/F), idade (SIH valor + COD_IDADE), município com 6 ou 7 dígitos, competência, CNES com 7 dígitos, tipo de unidade texto contra inteiro.
- Cuidados: AIH de continuação (IDENT = 5) é descartada; equipes desativadas são filtradas por DT_DESAT; consultas de demanda filtram por **residência**, as de oferta pelo município do estabelecimento.
- Limitação: desde o e-SUS APS, a produção da atenção básica vai para o **SISAB**, não para o SIA, então o SIA subestima a APS.
- O SIA de SP é **pesado** (pode levar horas). O notebook tem `USAR_SIA = False` para pular essa base.
- No claude.ai, o ambiente na nuvem não acessava o FTP do DATASUS. Em 28/10/2026 o notebook rodou localmente com dados reais (veja "Situação atual").

## Estrutura da pasta

```
enunciado/      PDFs da professora (enunciado do TP1 e exemplos de aula)
notebook/       dw_aps_sao_carlos.ipynb (ETL completo → DuckDB + 5 consultas OLAP)
                explorar_dados_sao_carlos.py (exploração rápida de 1 mês, gera relatorio_exploracao.txt)
esquemas/       PNGs das 3 estrelas e da constelação + especificacao_esquemas.md
esquemas/fontes gen.py (Graphviz) + .dot/.svg: regenerar os diagramas com `python gen.py` (precisa do graphviz)
relatorio/      entrega atual: .docx editável com o template do ICMC + PDF gerado dele
                (trabalho1_versao_antiga_sem_template.pdf = 1ª versão, só para referência)
relatorio/gerador  scripts que geram o .docx (veja abaixo)
apresentacao/   slides em HTML (20 min, 4 partes), estilo "boletim cobalto": apresentacao_cobalto.html (+ .pptx)
apresentacao/gerador  build.py junta slides.html + base.css + tema_*.css + deck.js; `python build.py` regenera o HTML
                      gerar_pptx.py → apresentacao_cobalto.pptx: fundo de cada slide sem texto (captura do HTML) + caixas de
                      texto nativas na posição/fonte do HTML (pptx_captura.js mede, gerar_pptx.js monta com pptxgenjs) + notas
```

Repositório público: https://github.com/germanojorge/dw-aps-sao-carlos (branch `main`). A cada push que mexe em `apresentacao/`,
o workflow `.github/workflows/slides.yml` roda o `build.py` e publica em https://germanojorge.github.io/dw-aps-sao-carlos/
(página inicial em `apresentacao/site/index.html`). O grupo edita o `slides.html` pelo site do GitHub; o passo a passo está no `README.md`.
Tudo está no repositório, inclusive os PDFs do enunciado e o DW pronto (`notebook/dados/dw_aps_sao_carlos.duckdb`); só ficam de fora o `.venv`, o `node_modules`, caches e logs.

### Como rodar

- **Notebook:** `pip install pysus duckdb pandas pyarrow requests matplotlib` (ou use `notebook/.venv`). Já vem com `MODO_TESTE = False` e com os dados de 2023–2024 em `dados/staging`, então roda sem baixar nada. Saída: `dados/dw_aps_sao_carlos.duckdb` + parquet em `dados/dw/`.
- **Gráficos dos slides:** depois de rodar o notebook, `cd apresentacao/gerador && ../../notebook/.venv/bin/python exportar_consultas.py && python build.py`.
- **Relatório .docx** (de dentro de `relatorio/gerador/`):
  1. editar o texto em `conteudo.py` (marcação simples: `<b>`, `<i>`, `<font name='Mono'>`);
  2. `python extrair.py`, que gera `conteudo.json`;
  3. `node gerar.js`, que gera `bruto.docx` (precisa de `npm install docx`; requer Pillow para o passo 2);
  4. opcional: `/usr/bin/python3 atualizar_indice.py bruto.docx final.docx conferencia.pdf`, que preenche o índice via LibreOffice (UNO; o módulo `uno` só existe no Python do sistema). Sem esse passo, o Word atualiza o índice ao abrir o arquivo. O erro "bridge already disposed" no fim é inofensivo: os arquivos já foram gravados.
  - As capturas do notebook na seção 3 ficam em `consultas/`. Para refazer depois de rodar o notebook: `../../notebook/.venv/bin/python capturar_consultas.py` (precisa de chromium e ImageMagick).
  - A capa (título, data, nomes) fica em `gerar.js`, não no `conteudo.py`.
- **Relatório em LaTeX** (mesmo conteúdo e template, figuras flutuantes): de dentro de `relatorio/gerador/`, `python extrair.py && python gerar_latex.py`. Precisa do `tectonic` (baixa os pacotes sozinho). Gera `latex/relatorio.tex` + `latex/figuras/` (pasta autocontida; no Overleaf, use XeLaTeX) e `latex/relatorio.pdf`, que é copiado para `relatorio/trabalho1_dw_atencao_basica_sao_carlos_latex.pdf`. A capa do LaTeX fica em `CAPA`, dentro do `gerar_latex.py`: ao mudar nomes ou data, mude lá e no `gerar.js`.
  - O template (`faixa.png` = faixa lateral, `header.png` = logo ICMC/USP) fica no cabeçalho, com posições medidas no PDF do enunciado. O rodapé leva o endereço do ICMC e o número da página.
  - Também dá para editar o `.docx` direto no Word. Nesse caso, o `conteudo.py` deixa de ser a fonte da verdade.

## Situação atual (28/10/2026)

Feito: tema e fontes, modelagem, diagramas, relatório em PDF e .docx, slides, e **o notebook rodado com dados reais de 2023–2024** (saídas salvas no .ipynb).

Dados reais e validação:
- Os dados já filtrados para São Carlos estão em `notebook/dados/staging/` (~13 MB) e `notebook/dados/referencia/` (IBGE, API do CNES). Com eles presentes, o notebook **não baixa nada** e roda em ~20 s. Não apague essas pastas. O DW pronto também está versionado (`notebook/dados/dw_aps_sao_carlos.duckdb` e `dw/`).
- Ambiente: `notebook/.venv` (uv). Para executar e salvar as saídas sem Jupyter aberto: `jupyter nbconvert --execute` não serve por causa do `%pip`; use um executor com nbclient que pule essa célula.
- DW: fato_equipe 1.686, fato_internacao 39.609, fato_producao_ambulatorial 193.723 linhas; todas as chaves resolvidas.
- Conferido contra o TabNet: AIHs de residentes em jan/2024 (1.287 lá contra 1.285 aqui, diferença = AIHs tipo 5 descartadas), abr/2023 e dez/2024 (diferença de 1 AIH); capítulo IX em jan/2024 bate exatamente.
- Lista de ICSAP conferida com o texto da Portaria 221/2008; códigos de equipe conferidos com o `EQUIPE.dbf` do TAB_CNES (incluídos 04, 22, 23).
- Correções feitas no ETL ao rodar com dados reais: coluna `IDEQUIPE` (não ID_EQUIPE); `DT_DESAT` é AAAAMM e 900001 = nunca desativada; competência do SIA = `PA_MVM` (mês de processamento); download com fallback direto no FTP do DATASUS (o PySUS devolvia lista vazia para 5 meses do SIH); tipos de unidade 67, 76 e 80.

Achados que afetam o texto do trabalho:
- **As UBS/USF de São Carlos têm produção zero no SIA em 2023–2024**: toda a produção da APS está no SISAB. A Consulta 5 mostra esse painel zerado e explica o motivo.
- O número de eSF ficou constante em 23 (cobertura estimada 31,1%) nos 24 meses, então o drill-across ainda não mostra relação entre oferta e ICSAP.
- Slides: as 5 consultas usam gráficos com os dados reais (`apresentacao/gerador/exportar_consultas.py` → `dados/consultas.json` → `graficos.py`).

Pendências antes da entrega:
- [ ] Capa: nomes e nº USP dos integrantes (marcados com `[Nome]`/`[Nº USP]` no `gerar.js`).
- [ ] Confirmar se a **notação dos diagramas** (estilo Kimball) é a da aula; se não for, refazer em `esquemas/fontes/gen.py`.
- [x] Relatório atualizado (28/10/2026): resultados reais e captura do notebook em cada consulta, carga e validação na Seção 1.5, achado do SISAB na 1.6. As edições manuais da capa (título "Atenção Primária a Saúde", data 29/10/2026, sem a linha "Curso") foram levadas para o `gerar.js`.
- [x] Apresentação: estilo escolhido = cobalto (o território foi removido em 28/10/2026; está no histórico do git). Nomes já em `PARTES` (`apresentacao/gerador/deck.js`): Ivan Sardon, Vinícius Morotti, Germano Jorge, Matheus Rodrigues; por decisão do grupo, os nomes aparecem só na capa. Notas do apresentador: tecla N.
