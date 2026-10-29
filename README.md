# Atenção primária à saúde em São Carlos

Trabalho Prático 1 de **SCC0245 – Processamento Analítico de Dados** (ICMC-USP, Profa. Cristina Dutra de Aguiar).

Um data warehouse que liga a **oferta de equipes de saúde** (CNES), a **produção ambulatorial** (SIA) e as
**internações por condições sensíveis à atenção primária** (SIH) em São Carlos, com dados reais e oficiais de 2023 e 2024.
O modelo é uma constelação de 3 tabelas de fatos e 9 dimensões, e as 5 consultas OLAP (roll-up, drill-down,
slice and dice, pivot e drill-across) rodam sobre o DW carregado.

## Entregáveis

| | |
|---|---|
| **Relatório** | [`relatorio/trabalho1_dw_atencao_basica_sao_carlos_latex.pdf`](relatorio/trabalho1_dw_atencao_basica_sao_carlos_latex.pdf) |
| **Slides** | https://germanojorge.github.io/dw-aps-sao-carlos/ (versão PowerPoint: [`apresentacao/apresentacao_cobalto.pptx`](apresentacao/apresentacao_cobalto.pptx)) |
| **Notebook** | [`notebook/dw_aps_sao_carlos.ipynb`](notebook/dw_aps_sao_carlos.ipynb): ETL completo (DATASUS → DuckDB) e as 5 consultas, com as saídas salvas |
| **Esquemas** | [`esquemas/`](esquemas/): diagramas das estrelas e da constelação, e a [especificação das dimensões](esquemas/especificacao_esquemas.md) |

## Como rodar o notebook

```bash
pip install pysus duckdb pandas pyarrow requests matplotlib
```

Depois, execute as células em ordem. Os dados de 2023–2024 já filtrados para São Carlos (~13 MB) ficam neste
repositório, em [`notebook/dados/staging/`](notebook/dados/staging) e [`notebook/dados/referencia/`](notebook/dados/referencia).
Se essas pastas não existirem ao lado do notebook (por exemplo, na cópia entregue sem os dados), a seção 1.1 do
notebook baixa os arquivos daqui. Com os dados no lugar, o notebook reconstrói o DW em cerca de 20 segundos, sem acessar o DATASUS.

Para baixar outro período direto do DATASUS, mude `ANOS` na configuração. O SIA de SP é pesado (pode levar horas);
`USAR_SIA = False` pula essa base.

## Consultar o DW sem rodar nada

O banco já carregado está em `notebook/dados/dw_aps_sao_carlos.duckdb` (e as tabelas em parquet em `notebook/dados/dw/`):

```python
import duckdb                                   # pip install duckdb
con = duckdb.connect("notebook/dados/dw_aps_sao_carlos.duckdb", read_only=True)
con.sql("SELECT * FROM fato_internacao LIMIT 5").show()
```

## Estrutura

| Pasta | O que tem |
|---|---|
| `notebook/` | ETL (PySUS → DuckDB), consultas OLAP e os dados de São Carlos já filtrados |
| `esquemas/` | Diagramas (PNG) e fontes Graphviz em `esquemas/fontes/` (`python gen.py` regenera) |
| `relatorio/` | Relatório em PDF e .docx (template do ICMC); geradores em `relatorio/gerador/` |
| `apresentacao/` | Slides em HTML e .pptx; gerador em `apresentacao/gerador/` |
| `apresentacao/roteiros/` | Roteiro de cada apresentador (partes 1 a 4), em .md e .docx |
| `enunciado/` | Enunciado do trabalho e exemplos de aula |

Os detalhes de cada parte estão no [`CLAUDE.md`](CLAUDE.md).

---

## Para o grupo: como editar os slides

Todo o texto dos slides está em um arquivo só: [`apresentacao/gerador/slides.html`](apresentacao/gerador/slides.html).

1. Abra o arquivo no GitHub e clique no lápis (**Edit this file**).
2. Ache o slide pelo comentário que o abre, por exemplo `<!-- 19 · Q1 ROLL-UP -->`, e mude o texto.
   - O que aparece na tela fica entre as tags (`<h2>…</h2>`, `<span>…</span>`).
   - As notas do apresentador ficam no atributo `data-notes="…"` de cada slide (tecla **N** mostra na apresentação).
   - Não apague as tags nem os marcadores entre chaves duplas, como `{{Q1}}` ou `{{ICON:users}}`: eles viram gráficos e ícones.
3. Clique em **Commit changes**. Em 1 ou 2 minutos o link dos slides mostra a versão nova
   (o andamento aparece na aba **Actions**; se ficar vermelho, a mudança quebrou algo e dá para desfazer pelo histórico).

Se duas pessoas forem mexer ao mesmo tempo, combinem quem fica com qual parte (cada parte é um bloco de slides).
O modo de edição dentro da apresentação (tecla **E**) só salva no seu computador: para valer para todos, edite pelo GitHub.

### Versão em PowerPoint

O [`.pptx`](apresentacao/apresentacao_cobalto.pptx) tem os textos editáveis e as notas do apresentador. Abre no PowerPoint
e no Google Slides (Arquivo → Importar slides). Formas, ícones, diagramas e gráficos são imagens de fundo; ao mudar um
texto, confira se ele ainda cabe na caixa desenhada atrás. No PowerPoint, instale as fontes gratuitas Newsreader,
Hanken Grotesk e DM Mono (Google Fonts); o Google Slides já as tem.

O .pptx é gerado a partir do HTML: depois de mudar o `slides.html`, rode `python build.py && python gerar_pptx.py`
em `apresentacao/gerador/` (precisa de chromium, ImageMagick, node e `npm install pptxgenjs`). Edições feitas direto
no .pptx não voltam para o HTML. Só para os slides em HTML, `python build.py` basta (precisa só de Python 3).
