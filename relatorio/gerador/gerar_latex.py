# Monta o relatório em LaTeX (latex/relatorio.tex) a partir do conteudo.json gerado pelo extrair.py
# e compila com o Tectonic. Mesmo template do .docx: faixa lateral, logo no cabeçalho, endereço no rodapé.
# Rode de dentro desta pasta:  python extrair.py && python gerar_latex.py
# Para editar no Overleaf: suba a pasta latex/ inteira e escolha o compilador XeLaTeX.
import json, os, shutil, subprocess
from pathlib import Path

os.chdir(Path(__file__).resolve().parent)
BLOCOS = json.load(open("conteudo.json", encoding="utf-8"))
SAIDA = Path("latex")
FIG = SAIDA / "figuras"          # cópias das imagens: a pasta latex/ fica autocontida (dá para subir no Overleaf)
FIG.mkdir(parents=True, exist_ok=True)
for arq in ("faixa.png", "header.png"):
    shutil.copy(arq, FIG / arq)

# ---------- texto ----------
ESPECIAIS = {"\\": r"\textbackslash{}", "{": r"\{", "}": r"\}", "$": r"\$", "&": r"\&", "#": r"\#",
             "^": r"\^{}", "_": r"\_", "%": r"\%", "~": r"\~{}"}

def esc(t, mono=False):
    # identificadores longos (fato_producao_ambulatorial) podem quebrar depois do sublinhado
    return "".join(ESPECIAIS.get(c, c) for c in t).replace(r"\_", r"\_\allowbreak{}")

def runs(rs):
    out = []
    for r in rs:
        t = esc(r["t"], r["m"])
        if r["m"]: t = r"\texttt{" + t + "}"
        if r["i"]: t = r"\textit{" + t + "}"
        if r["b"]: t = r"\textbf{" + t + "}"
        out.append(t)
    return "".join(out)

def plano(rs):
    return "".join(r["t"] for r in rs)

# ---------- blocos ----------
def tabela(b):
    total = sum(b["w"])
    n = len(b["w"])
    # larguras proporcionais às do .docx, descontando o espaço entre colunas
    cols = "|".join(rf">{{\raggedright\arraybackslash}}p{{\dimexpr{w / total:.4f}\linewidth-2\tabcolsep-{(n + 1) / n:.2f}\arrayrulewidth\relax}}"
                    for w in b["w"])
    cab = " & ".join(r"\color{white}\bfseries " + runs(c) for c in b["head"]) + r" \\ \hline"
    linhas = "\n".join(" & ".join(runs(c) for c in l) + r" \\ \hline" for l in b["rows"])
    if b["keep"]:   # tabela curta: não quebra entre páginas
        return (r"\par\noindent\begin{minipage}{\linewidth}\small\rowcolors{2}{white}{linhapar}"
                rf"\begin{{tabular}}{{|{cols}|}}\hline\rowcolor{{azul}}{cab}" "\n" + linhas +
                r"\end{tabular}\end{minipage}\par\medskip")
    return (r"{\small\rowcolors{2}{white}{linhapar}" rf"\begin{{longtable}}{{|{cols}|}}\hline\rowcolor{{azul}}{cab}\endhead"
            "\n" + linhas + r"\end{longtable}}")

def figura(img, legenda, pagina_cheia=False):
    caminho = Path("figuras") / Path(img["path"]).name
    shutil.copy(img["path"], SAIDA / caminho)
    # capturas das consultas podem ocupar a página toda (sobra espaço só para a legenda)
    altura = r"\dimexpr\textheight-4\baselineskip\relax" if pagina_cheia else f"{img['max_h']}cm"
    return (r"\begin{figure}[!htbp]\centering" "\n"
            rf"\includegraphics[width=\linewidth,height={{{altura}}},keepaspectratio]{{{caminho.as_posix()}}}" "\n"
            rf"\legenda{{{runs(legenda['r'])}}}" "\n" r"\end{figure}")

def montar(blocos):
    """Converte a lista de blocos em LaTeX. Agrupa marcadores e hierarquias consecutivos."""
    out, i, secao = [], 0, ""
    while i < len(blocos):
        b = blocos[i]
        k = b["k"]
        if k == "h1":
            secao = plano(b["r"])
            out.append(r"\FloatBarrier\section*{" + runs(b["r"]) + "}" + r"\addcontentsline{toc}{section}{" + runs(b["r"]) + "}")
        elif k == "h2":
            out.append(r"\FloatBarrier\subsection*{" + runs(b["r"]) + "}" + r"\addcontentsline{toc}{subsection}{" + runs(b["r"]) + "}")
            if secao.startswith("3"):
                # Nas consultas, a figura entra logo após o título: como é flutuante, o LaTeX a leva para o
                # topo da página seguinte se não couber, e o texto da consulta preenche o espaço que sobraria.
                j = i + 1
                while j < len(blocos) and blocos[j]["k"] not in ("h1", "h2"):
                    if blocos[j]["k"] == "img":
                        out.append(figura(blocos[j], blocos[j + 1], pagina_cheia=True))
                    j += 1
        elif k == "h3":
            out.append(r"\subsubsection*{" + runs(b["r"]) + "}")
        elif k == "p":
            out.append(runs(b["r"]) + "\n")
        elif k == "pbold":
            out.append(r"\textbf{" + runs(b["r"]) + r"}\par\nopagebreak\smallskip")
        elif k == "bullet":
            itens = []
            while i < len(blocos) and blocos[i]["k"] == "bullet":
                itens.append(r"\item " + runs(blocos[i]["r"]))
                i += 1
            out.append(r"\begin{itemize}" + "\n".join(itens) + r"\end{itemize}")
            continue
        elif k == "hier":
            linhas = []
            while i < len(blocos) and blocos[i]["k"] == "hier":
                linhas.append(r"\texttt{" + esc(plano(blocos[i]["r"]), True) + "}")
                i += 1
            out.append(r"\begin{hierarquias}" + r"\\".join(linhas) + r"\end{hierarquias}")
            continue
        elif k == "img":
            if not secao.startswith("3"):          # nas consultas a figura já foi posta após o título
                out.append(figura(b, blocos[i + 1]))
            i += 2                                  # pula a legenda junto
            continue
        elif k == "caption":
            pass                                    # legendas órfãs não existem; tratadas em figura()
        elif k == "pagebreak":
            out.append(r"\clearpage")
        elif k == "table":
            out.append(tabela(b))
        else:
            raise ValueError("bloco desconhecido: " + k)
        i += 1
    return "\n\n".join(out)

# ---------- documento ----------
PREAMBULO = r"""\documentclass[12pt,a4paper]{article}
\usepackage[brazil]{babel}
\usepackage{fontspec}
% fontes pelo nome do arquivo (o Tectonic as traz no pacote, mas não pelo nome da família)
\setmainfont{texgyretermes}[Extension=.otf,UprightFont=*-regular,BoldFont=*-bold,ItalicFont=*-italic,BoldItalicFont=*-bolditalic]
\setsansfont{texgyreheros}[Extension=.otf,UprightFont=*-regular,BoldFont=*-bold,ItalicFont=*-italic,BoldItalicFont=*-bolditalic]
\setmonofont{texgyrecursor}[Scale=0.92,Extension=.otf,UprightFont=*-regular,BoldFont=*-bold,ItalicFont=*-italic,BoldItalicFont=*-bolditalic]
\usepackage{amssymb,newunicodechar}
\newunicodechar{≤}{\ensuremath{\leq}}
\newunicodechar{→}{\ensuremath{\rightarrow}}
\newunicodechar{✓}{\ensuremath{\checkmark}}
\usepackage[a4paper,top=110pt,bottom=95pt,left=85pt,right=80pt,headheight=14pt,footskip=40pt]{geometry}
\usepackage[table]{xcolor}
\definecolor{azul}{HTML}{1F3864}
\definecolor{cinzarodape}{HTML}{6B809B}
\definecolor{linhapar}{HTML}{F2F5FA}
\definecolor{bordatab}{HTML}{B4B4B4}
\arrayrulecolor{bordatab}
\usepackage{graphicx,eso-pic,fancyhdr,longtable,array,enumitem,setspace,placeins,microtype}
\usepackage[explicit]{titlesec}
\usepackage{tocloft}
\usepackage[hidelinks]{hyperref}

\setstretch{1.15}
\setlength{\parindent}{0pt}
\setlength{\parskip}{6pt}
\setlength{\emergencystretch}{2em}
\renewcommand{\arraystretch}{1.25}
\setlist[itemize]{label=\textbullet,leftmargin=20pt,itemsep=3pt,topsep=2pt}

% títulos (a numeração já vem no texto)
\titleformat{\section}{\color{azul}\bfseries\fontsize{16}{19}\selectfont}{}{0pt}{#1}
\titleformat{\subsection}{\color{azul}\bfseries\fontsize{13}{16}\selectfont}{}{0pt}{#1}
\titleformat{\subsubsection}{\bfseries\normalsize}{}{0pt}{#1}
\titlespacing*{\section}{0pt}{6pt}{10pt}
\titlespacing*{\subsection}{0pt}{12pt}{6pt}
\titlespacing*{\subsubsection}{0pt}{9pt}{4pt}

% índice
\addto\captionsbrazil{\renewcommand{\contentsname}{Índice}}
\renewcommand{\cfttoctitlefont}{\color{azul}\bfseries\fontsize{16}{19}\selectfont}
\renewcommand{\cftsecleader}{\cftdotfill{\cftdotsep}}
\renewcommand{\cftsecfont}{\normalfont}
\renewcommand{\cftsecpagefont}{\normalfont}
\setlength{\cftsubsecindent}{18pt}
\setlength{\cftbeforesecskip}{3pt}

% figuras: legenda em itálico, centralizada (o texto já traz "Figura N –")
\newcommand{\legenda}[1]{\par\vspace{4pt}{\small\itshape #1\par}}
\renewcommand{\topfraction}{0.95}
\renewcommand{\bottomfraction}{0.6}
\renewcommand{\textfraction}{0.05}
\renewcommand{\floatpagefraction}{0.75}
\setlength{\textfloatsep}{14pt plus 4pt minus 2pt}
\setlength{\floatsep}{12pt plus 4pt minus 2pt}

% hierarquias em fonte mono, recuadas
\newenvironment{hierarquias}{\par\nopagebreak\leftskip=20pt\small\setlength{\parskip}{0pt}}{\par\medskip}

% template do ICMC: faixa lateral e logo (posições em pt medidas no PDF do enunciado)
\AddToShipoutPictureBG{\AtPageUpperLeft{%
  \put(5,-837.9){\includegraphics[width=69.8pt,height=831.9pt]{figuras/faixa.png}}%
  \put(73.6,-85.5){\includegraphics[width=522.6pt,height=63.6pt]{figuras/header.png}}}}
\newcommand{\rodapeicmc}{{\sffamily\fontsize{8}{10}\selectfont\color{cinzarodape}Av. Trabalhador São-carlense, 400 . centro . São Carlos - SP . cep 13566-590 . Brasil . www.icmc.usp.br}}
\fancypagestyle{icmc}{\fancyhf{}\renewcommand{\headrulewidth}{0pt}%
  \fancyfoot[C]{\hfill{\sffamily\fontsize{8}{10}\selectfont\color{cinzarodape}\thepage}\\[3pt]\rodapeicmc}}
\fancypagestyle{capa}{\fancyhf{}\renewcommand{\headrulewidth}{0pt}\fancyfoot[C]{\rodapeicmc}}
\pagestyle{icmc}
"""

CAPA = r"""\begin{titlepage}\thispagestyle{capa}\centering\setstretch{1.1}
\vspace*{10pt}
{\bfseries Departamento de Ciências de Computação – SCC\\
Instituto de Ciências Matemáticas e de Computação – ICMC\\
Universidade de São Paulo – USP\\
Disciplina SCC0245 – Processamento Analítico de Dados\\[10pt]
Docente Responsável: Profa. Cristina Dutra de Aguiar\par}
\vspace{60pt}
{\bfseries\fontsize{13}{16}\selectfont Trabalho Prático 1\par}\vspace{10pt}
{\color{azul}\bfseries\fontsize{18}{22}\selectfont Data Warehouse para Análise da Cobertura da\\ Atenção Primária a Saúde em São Carlos\par}\vspace{8pt}
{\itshape Unidades e equipes de saúde, demanda ambulatorial e internações evitáveis\par}
\vspace{60pt}
{\arrayrulecolor{gray}\renewcommand{\arraystretch}{1.5}
\begin{tabular}{|p{0.62\linewidth}|p{0.22\linewidth}|}\hline
\rowcolor[HTML]{E8EDF5}\textbf{Integrante} & \textbf{Nº USP} \\ \hline
Ivan Sardon Medina & [Nº USP] \\ \hline
Vinícius Morotti & [Nº USP] \\ \hline
Germano Antonio Zani Jorge & [Nº USP] \\ \hline
Matheus Rodrigues & [Nº USP] \\ \hline
\end{tabular}\par}
\vfill
São Carlos, 29 de Outubro de 2026\par
\vspace{30pt}
\end{titlepage}
"""

doc = (PREAMBULO + r"\begin{document}" "\n" + CAPA +
       r"\setcounter{page}{2}\tableofcontents\clearpage" "\n\n" + montar(BLOCOS) + "\n\n" r"\end{document}" "\n")
(SAIDA / "relatorio.tex").write_text(doc, encoding="utf-8")

subprocess.run(["tectonic", "-X", "compile", "--keep-logs", "relatorio.tex"], cwd=SAIDA, check=True)
final = Path("..") / "trabalho1_dw_atencao_basica_sao_carlos_latex.pdf"
shutil.copy(SAIDA / "relatorio.pdf", final)
print("ok:", final.resolve())
