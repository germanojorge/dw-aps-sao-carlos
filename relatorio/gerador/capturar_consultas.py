# Gera as capturas das consultas do notebook (consultas/*.png) usadas na seção 3 do relatório.
# Rode depois de executar o notebook, de dentro desta pasta, com o Python do venv do notebook:
#     ../../notebook/.venv/bin/python capturar_consultas.py
# Precisa de chromium e ImageMagick (magick) instalados.
import copy, subprocess, sys, tempfile
from pathlib import Path
import nbformat

AQUI = Path(__file__).resolve().parent
NB = AQUI.parent.parent / "notebook" / "dw_aps_sao_carlos.ipynb"
SAIDA = AQUI / "consultas"
JUPYTER = Path(sys.executable).parent / "jupyter"

# célula do notebook -> (arquivo, largura da janela em px). A pivot rotacionada é larga, por isso a janela maior.
CELULAS = {24: ("consulta1", 820), 26: ("consulta2", 820), 28: ("consulta3", 820),
           30: ("consulta4", 1060), 32: ("consulta5", 820), 33: ("consulta5_grafico", 1180)}
QUEBRA = "<style>pre,.highlight pre{white-space:pre-wrap!important;word-break:break-word}</style></head>"
SEM_CODIGO = "<style>.jp-Cell-inputWrapper,.jp-InputArea,.jp-OutputPrompt{display:none!important}</style></head>"

nb = nbformat.read(NB, as_version=4)
SAIDA.mkdir(exist_ok=True)
with tempfile.TemporaryDirectory() as tmp:
    tmp = Path(tmp)
    for i, (nome, largura) in CELULAS.items():
        mini = copy.deepcopy(nb)
        mini.cells = [nb.cells[i]]
        nbformat.write(mini, tmp / f"{nome}.ipynb")
        subprocess.run([str(JUPYTER), "nbconvert", "--to", "html", "--template", "lab", str(tmp / f"{nome}.ipynb")],
                       check=True, capture_output=True)
        html = tmp / f"{nome}.html"
        estilo = QUEBRA if nome != "consulta5_grafico" else SEM_CODIGO   # no gráfico, só a figura
        html.write_text(html.read_text().replace("</head>", estilo, 1))
        bruto = tmp / f"{nome}.png"
        subprocess.run(["chromium", "--headless=new", "--disable-gpu", "--hide-scrollbars",
                        f"--force-device-scale-factor={2.5 if largura == 820 else 2}", f"--window-size={largura},3600", "--virtual-time-budget=3000",
                        f"--screenshot={bruto}", html.as_uri()], check=True, capture_output=True)
        subprocess.run(["magick", str(bruto), "-fuzz", "2%", "-trim", "+repage",
                        "-bordercolor", "white", "-border", "24", str(SAIDA / f"{nome}.png")], check=True)
        print("ok:", nome)
