# Atenção primária à saúde em São Carlos

Trabalho Prático 1 de **SCC0245 – Processamento Analítico de Dados** (ICMC-USP): um data warehouse que liga
equipes de saúde (CNES), produção ambulatorial (SIA) e internações evitáveis (SIH) em São Carlos, 2023–2024.

**Slides:** https://germanojorge.github.io/dw-aps-sao-carlos/

## Como editar os slides

Todo o texto dos slides está em um arquivo só: [`apresentacao/gerador/slides.html`](apresentacao/gerador/slides.html).

1. Abra o arquivo no GitHub e clique no lápis (**Edit this file**).
2. Ache o slide pelo comentário que o abre, por exemplo `<!-- 20 · Q1 ROLL-UP -->`, e mude o texto.
   - O que aparece na tela fica entre as tags (`<h2>…</h2>`, `<span>…</span>`).
   - As notas do apresentador ficam no atributo `data-notes="…"` de cada slide (tecla **N** mostra na apresentação).
   - Não apague as tags nem os marcadores entre chaves duplas, como `{{Q1}}` ou `{{ICON:users}}`: eles viram gráficos e ícones.
3. Clique em **Commit changes**. Em 1 ou 2 minutos o link acima mostra a versão nova
   (o andamento aparece na aba **Actions**; se ficar vermelho, a mudança quebrou algo e dá para desfazer pelo histórico).

Dicas: se duas pessoas forem mexer ao mesmo tempo, combinem quem fica com qual parte (cada parte é um bloco de slides).
O modo de edição dentro da apresentação (tecla **E**) só salva no seu computador: para valer para todos, edite pelo GitHub.

## Versão em PowerPoint

[`apresentacao/apresentacao_cobalto.pptx`](apresentacao/apresentacao_cobalto.pptx) (também na página dos slides): estilo cobalto,
com os textos editáveis e as notas do apresentador. Abre no PowerPoint e no Google Slides (Arquivo → Importar slides).
Formas, ícones, diagramas e gráficos são imagens de fundo; ao mudar um texto, confira se ele ainda cabe na caixa desenhada atrás.
No PowerPoint, instale as fontes gratuitas Newsreader, Hanken Grotesk e DM Mono (Google Fonts); o Google Slides já as tem.

O .pptx é gerado a partir do HTML: depois de mudar o `slides.html`, rode `python build.py && python gerar_pptx.py`
em `apresentacao/gerador/` (precisa de chromium, ImageMagick, node e `npm install pptxgenjs`). Edições feitas direto no
.pptx não voltam para o HTML.

## Estrutura

| Pasta | O que tem |
|---|---|
| `notebook/` | ETL completo (PySUS → DuckDB) e as 5 consultas OLAP. Os dados de São Carlos já filtrados estão em `notebook/dados/staging/`, então o notebook roda sem baixar nada. |
| `esquemas/` | Diagramas das estrelas e da constelação, e a especificação das dimensões |
| `relatorio/` | Relatório em .docx/PDF (template do ICMC) e versão em LaTeX; geradores em `relatorio/gerador/` |
| `apresentacao/` | Slides em HTML (estilo cobalto) e a versão .pptx; gerador em `apresentacao/gerador/` |
| `apresentacao/roteiros/` | Roteiro de cada apresentador (partes 1 a 4): explicação de cada slide e uma fala de exemplo, em .md e .docx |

## Consultar o DW sem rodar nada

O banco já carregado está em `notebook/dados/dw_aps_sao_carlos.duckdb` (e as tabelas em parquet em `notebook/dados/dw/`):

```python
import duckdb                                   # pip install duckdb
con = duckdb.connect("notebook/dados/dw_aps_sao_carlos.duckdb", read_only=True)
con.sql("SELECT * FROM fato_internacao LIMIT 5").show()
```

Para rodar o notebook: `pip install pysus duckdb pandas pyarrow requests matplotlib` e executar as células em ordem
(usa os dados já salvos em `notebook/dados/staging/`, sem download, em ~20 s).

Rodar localmente: `cd apresentacao/gerador && python build.py` regenera os slides (só precisa de Python 3).
Os detalhes de cada parte estão no [`CLAUDE.md`](CLAUDE.md).
