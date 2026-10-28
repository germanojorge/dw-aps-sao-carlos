"""
Gera apresentacao/apresentacao_cobalto.pptx a partir do deck HTML (rode o build.py antes).

Cada slide vira: uma imagem de fundo com tudo que não é texto (formas, ícones, mapas, diagramas, gráficos)
+ caixas de texto nativas, editáveis, na mesma posição, fonte, tamanho e cor do HTML + notas do apresentador.

Uso (de dentro de apresentacao/gerador/):  python gerar_pptx.py
Precisa de chromium, ImageMagick (magick), node e do pacote pptxgenjs (npm install pptxgenjs, nesta pasta).
"""
import json, re, subprocess, tempfile
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DECK = AQUI.parent / "apresentacao_cobalto.html"
SAIDA = AQUI.parent / "apresentacao_cobalto.pptx"
CAPTURA_JS = (AQUI / "pptx_captura.js").read_text()

# Na captura: sem animações nem contadores, tudo no estado final, sem a interface do deck
CSS_CAPTURA = """<style>
*, *::before, *::after { transition: none !important; animation: none !important; }
.rv { opacity: 1 !important; transform: none !important; }
#progress, .edit-hotzone, #editToggle, #notes { display: none !important; }
u { text-decoration: none !important; }
</style>"""

FONTES = ["400 20px Newsreader", "500 20px Newsreader", "italic 400 20px Newsreader", "400 20px \\'Hanken Grotesk\\'",
          "500 20px \\'Hanken Grotesk\\'", "600 20px \\'Hanken Grotesk\\'", "400 20px \\'DM Mono\\'", "500 20px \\'DM Mono\\'"]

def copia_captura(modo, destino):
    html = DECK.read_text()
    html = re.sub(r'\sdata-count="\d+"', "", html)          # contador animado reescreveria o texto
    html = html.replace("<html", f'<html data-captura="{modo}"', 1)
    html = html.replace("</head>", CSS_CAPTURA + "</head>", 1)
    # mede só depois que as fontes da web carregarem (com a fonte reserva as posições mudam)
    carregar = ",".join(f"document.fonts.load('{f}')" for f in FONTES)
    html = html.replace("</body>", f"<script>Promise.all([{carregar}]).then(function(){{return document.fonts.ready}})"
                        ".then(function(){setTimeout(function(){" + CAPTURA_JS + "}, 500)})</script></body>", 1)
    destino.write_text(html)

def chromium(*args):
    return subprocess.run(["chromium", "--headless=new", "--disable-gpu", "--hide-scrollbars",
                           "--window-size=1920,1080", "--virtual-time-budget=6000", *args],
                          check=True, capture_output=True, text=True).stdout

with tempfile.TemporaryDirectory() as tmp:
    tmp = Path(tmp)
    # 1) textos: posições e estilos de todos os slides
    copia_captura("texto", tmp / "texto.html")
    dom = chromium("--dump-dom", (tmp / "texto.html").as_uri())
    m = re.search(r'<pre id="__saida">(.*?)</pre>', dom, re.S)
    assert m, "a captura dos textos não rodou (veja o pptx_captura.js)"
    slides = json.loads(m.group(1).replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&"))

    # 2) fundos: cada slide sem os textos, em 2x para os gráficos ficarem nítidos
    copia_captura("fundo", tmp / "fundo.html")
    for s in slides:
        png = tmp / f"f{s['n']:02d}.png"
        chromium("--force-device-scale-factor=2", f"--screenshot={png}", (tmp / "fundo.html").as_uri() + f"#{s['n']}")
        s["fundo"] = str(tmp / f"f{s['n']:02d}.jpg")
        subprocess.run(["magick", str(png), "-quality", "90", s["fundo"]], check=True)

    (tmp / "slides.json").write_text(json.dumps(slides, ensure_ascii=False))
    subprocess.run(["node", str(AQUI / "gerar_pptx.js"), str(tmp / "slides.json"), str(SAIDA)], check=True, cwd=AQUI)
print("ok:", SAIDA)
