"""
Gera a apresentação no estilo "boletim cobalto":
    ../apresentacao_cobalto.html     (papel creme quadriculado + azul-cobalto)

Uso (de dentro de apresentacao/gerador/):
    python build.py

Arquivos de entrada:
    slides.html          conteúdo dos slides (texto, ordem, notas do apresentador em data-notes)
    base.css             componentes dos slides
    tema_cobalto.css     cores, fontes e decoração do estilo "boletim cobalto"
    deck.js              navegação, escala 16:9, notas (tecla N) e edição inline (tecla E)
    icones/*.svg         ícones Lucide (licença ISC)
    dados/               contorno de São Carlos (API de malhas do IBGE) e UBS (API de Dados Abertos do CNES)

Marcadores aceitos em slides.html:
    {{ICON:nome}}  {{MAPA}}  {{MAPA_ZOOM}}  {{ESTRELA:fato}}  {{CONSTELACAO}}  {{CUBO}}  {{GLITCH}}  {{Q1}}…{{Q5}} (graficos.py)
"""
import json, math, re
from pathlib import Path

AQUI = Path(__file__).parent
SAIDA = AQUI.parent

# ---------------------------------------------------------------- ícones
def icone(nome):
    svg = (AQUI / "icones" / f"{nome}.svg").read_text()
    svg = re.sub(r"<!--.*?-->", "", svg, flags=re.S).strip()
    tag_fim = svg.index(">") + 1   # remove class/width/height só da tag <svg> raiz
    raiz = re.sub(r'\s(class|width|height)="[^"]*"', "", svg[:tag_fim])
    return raiz.replace("<svg", f'<svg class="ic ic-{nome}"', 1) + svg[tag_fim:]

# ---------------------------------------------------------------- mapa de São Carlos
LAT0 = math.radians(-22.0)
geo = json.loads((AQUI / "dados" / "sao_carlos_ibge.geojson").read_text())
anel = geo["features"][0]["geometry"]["coordinates"][0]
xs = [lon * math.cos(LAT0) for lon, _ in anel]
ys = [-lat for _, lat in anel]
MINX, MINY = min(xs), min(ys)
ESC = 1000 / (max(xs) - MINX)
ALT = (max(ys) - MINY) * ESC

def proj(lon, lat):
    return ((lon * math.cos(LAT0) - MINX) * ESC, (-lat - MINY) * ESC)

PATH_SC = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in (proj(lon, lat) for lon, lat in anel)) + "Z"
ubs = json.loads((AQUI / "dados" / "ubs_api_cnes.json").read_text())
pts = [proj(u["lon"], u["lat"]) for u in ubs if u["lat"] and u["lon"]]

# recorte da área urbana (onde está a maioria das unidades)
ZX0, ZY0 = proj(-47.935, -21.975)
ZX1, ZY1 = proj(-47.845, -22.075)

def mapa():
    dots = "".join(f'<circle class="ubs" cx="{x:.1f}" cy="{y:.1f}" r="11" style="--i:{i}"/>' for i, (x, y) in enumerate(pts))
    return (f'<svg class="mapa" viewBox="0 0 1000 {ALT:.0f}"><path class="mun" d="{PATH_SC}"/>'
            f'<rect class="zoombox" x="{ZX0:.0f}" y="{ZY0:.0f}" width="{ZX1-ZX0:.0f}" height="{ZY1-ZY0:.0f}"/>{dots}</svg>')

def mapa_zoom():
    w, h = ZX1 - ZX0, ZY1 - ZY0
    dots = "".join(f'<circle class="ubs" cx="{x:.1f}" cy="{y:.1f}" r="{w/70:.1f}" style="--i:{i}"/>' for i, (x, y) in enumerate(pts))
    return (f'<svg class="mapa-zoom" viewBox="{ZX0:.1f} {ZY0:.1f} {w:.1f} {h:.1f}" preserveAspectRatio="xMidYMid slice">'
            f'<path class="mun" d="{PATH_SC}"/>{dots}</svg>')

# ---------------------------------------------------------------- esquemas estrela
DIMS = {
    "dim_tempo": ["ano_mes", "trimestre", "semestre", "ano"],
    "dim_estabelecimento": ["cnes", "tipo_unidade", "nivel_atencao", "bairro"],
    "dim_tipo_equipe": ["tipo_equipe", "categoria_equipe"],
    "dim_procedimento": ["cod_procedimento", "subgrupo_cod", "grupo"],
    "dim_diagnostico": ["cid", "capitulo", "grupo_icsap", "icsap"],
    "dim_perfil_paciente": ["sexo", "faixa_etaria", "ciclo_vida"],
    "dim_localidade": ["municipio", "regiao_imediata", "uf"],
    "dim_junk_internacao": ["carater", "obito", "uti"],
    "dim_cbo": ["cbo", "familia_cbo", "categoria"],
}
FATOS = {
    "fato_equipe": (["dim_tempo", "dim_estabelecimento", "dim_tipo_equipe"],
                    [("DD", "id_equipe"), ("·", "COUNT(*)")]),
    "fato_internacao": (["dim_tempo", "dim_estabelecimento", "dim_procedimento", "dim_diagnostico",
                         "dim_perfil_paciente", "dim_localidade", "dim_junk_internacao"],
                        [("DD", "n_aih"), ("M", "qtd_internacoes"), ("M", "dias_permanencia"), ("M", "valor_total")]),
    "fato_producao_ambulatorial": (["dim_tempo", "dim_estabelecimento", "dim_procedimento",
                                    "dim_perfil_paciente", "dim_localidade", "dim_cbo"],
                                   [("M", "qtd_apresentada"), ("M", "qtd_aprovada"),
                                    ("M", "valor_apresentado"), ("M", "valor_aprovado")]),
}

def caixa_dim(nome, cx, cy, extra=""):
    attrs = DIMS[nome]
    w, lh = max(320, int(len(nome) * 17.5 + 44)), 34
    h = 56 + lh * len(attrs)
    x, y = cx - w / 2, cy - h / 2
    s = f'<g class="st-dim {extra}"><rect x="{x:.0f}" y="{y:.0f}" width="{w}" height="{h}" rx="6"/>'
    s += f'<text class="st-dname" x="{cx:.0f}" y="{y + 38:.0f}">{nome}</text>'
    for i, a in enumerate(attrs):
        s += f'<text class="st-attr" x="{cx:.0f}" y="{y + 38 + lh * (i + 1):.0f}">{a}</text>'
    return s + "</g>"

def estrela(fato):
    dims, medidas = FATOS[fato]
    W, H = 1640, 820
    cx, cy = W / 2, H / 2
    rx, ry = 620, 300
    n = len(dims)
    pos = []
    for i in range(n):
        ang = -math.pi / 2 + 2 * math.pi * i / n + (math.pi / n if n % 2 == 0 else 0)
        pos.append((cx + rx * math.cos(ang), cy + ry * math.sin(ang)))
    linhas = "".join(f'<line class="st-line" x1="{cx:.0f}" y1="{cy:.0f}" x2="{x:.0f}" y2="{y:.0f}" style="--i:{i}"/>'
                     for i, (x, y) in enumerate(pos))
    fw, lh = max(420, int(len(fato) * 19.5 + 60)), 38
    fh = 66 + lh * len(medidas)
    fx, fy = cx - fw / 2, cy - fh / 2
    f = f'<g class="st-fact"><rect x="{fx:.0f}" y="{fy:.0f}" width="{fw}" height="{fh}" rx="8"/>'
    f += f'<text class="st-fname" x="{cx:.0f}" y="{fy + 44:.0f}">{fato}</text>'
    for i, (tag, m) in enumerate(medidas):
        f += (f'<text class="st-meas" x="{fx + 30:.0f}" y="{fy + 44 + lh * (i + 1):.0f}">'
              f'<tspan class="st-tag">{tag}</tspan>  {m}</text>')
    f += "</g>"
    caixas = "".join(caixa_dim(d, x, y) for d, (x, y) in zip(dims, pos))
    return f'<svg class="estrela" viewBox="0 0 {W} {H}">{linhas}{caixas}{f}</svg>'

# ---------------------------------------------------------------- constelação
def constelacao():
    W, H = 1720, 800
    F = {"fato_equipe": (200, 400), "fato_producao_ambulatorial": (690, 400), "fato_internacao": (1510, 400)}
    D = {  # dimensão: (x, y, compartilhada?)
        "dim_tempo": (450, 100, True), "dim_estabelecimento": (1080, 100, True),
        "dim_perfil_paciente": (1130, 400, True), "dim_procedimento": (960, 700, True),
        "dim_localidade": (1300, 700, True),
        "dim_tipo_equipe": (200, 700, False), "dim_cbo": (620, 700, False),
        "dim_diagnostico": (1580, 700, False), "dim_junk_internacao": (1560, 100, False),
    }
    s, k = "", 0
    for fato, (fx, fy) in F.items():
        for d in FATOS[fato][0]:
            x, y, _ = D[d]
            s += f'<line class="cs-line" x1="{fx}" y1="{fy}" x2="{x}" y2="{y}" style="--i:{k}"/>'
            k += 1
    for d, (x, y, comp) in D.items():
        w = 14 * len(d) + 40
        s += (f'<g class="cs-dim{" shared" if comp else ""}"><rect class="fundo" x="{x - w / 2:.0f}" y="{y - 30}" width="{w}" height="60" rx="30"/>'
              f'<rect x="{x - w / 2:.0f}" y="{y - 30}" width="{w}" height="60" rx="30"/>'
              f'<text x="{x}" y="{y + 9}">{d}</text></g>')
    for fato, (fx, fy) in F.items():
        w = 15 * len(fato) + 56
        s += (f'<g class="cs-fact"><rect x="{fx - w / 2:.0f}" y="{fy - 42}" width="{w}" height="84" rx="8"/>'
              f'<text x="{fx}" y="{fy + 10}">{fato}</text></g>')
    return f'<svg class="constelacao" viewBox="0 0 {W} {H}">{s}</svg>'

# ---------------------------------------------------------------- cubo (slice and dice)
def cubo():
    u = 92
    c30, s30 = math.cos(math.pi / 6), 0.5
    ox, oy = 470, 330

    def p(x, y, z):  # x = ciclo de vida, z = diagnóstico, y = ano (para cima)
        return (ox + (x - z) * c30 * u, oy + (x + z) * s30 * u - y * u)

    def poly(pts_, cls):
        return f'<polygon class="{cls}" points="{" ".join(f"{a:.1f},{b:.1f}" for a, b in pts_)}"/>'

    cubos = [(x, y, z) for y in range(2) for z in range(4) for x in range(4)]
    cubos.sort(key=lambda c: (c[0] + c[2], c[1]))  # pintor: de trás para frente
    s = ""
    for x, y, z in cubos:
        cls = "cell"
        if y == 1:
            cls += " slice"
            if x == 3 and z < 3:
                cls += " dice"
        top = [p(x, y + 1, z), p(x + 1, y + 1, z), p(x + 1, y + 1, z + 1), p(x, y + 1, z + 1)]
        right = [p(x + 1, y, z), p(x + 1, y + 1, z), p(x + 1, y + 1, z + 1), p(x + 1, y, z + 1)]
        left = [p(x, y, z + 1), p(x + 1, y, z + 1), p(x + 1, y + 1, z + 1), p(x, y + 1, z + 1)]
        s += f'<g class="{cls}">{poly(top, "f-top")}{poly(right, "f-r")}{poly(left, "f-l")}</g>'
    # rótulos dos eixos
    ax = p(4.3, 0, 0); az = p(0, 0, 4.3); ay = p(0, 2.25, 0)
    s += f'<text class="ax" x="{ax[0]:.0f}" y="{ax[1] + 30:.0f}">ciclo de vida →</text>'
    s += f'<text class="ax" x="{az[0] - 10:.0f}" y="{az[1] + 30:.0f}" text-anchor="end">← diagnóstico</text>'
    s += f'<text class="ax" x="{ay[0]:.0f}" y="{ay[1] - 14:.0f}" text-anchor="middle">ano ↑</text>'
    return f'<svg class="cubo" viewBox="0 0 940 760">{s}</svg>'

# ---------------------------------------------------------------- coluna "glitch" (só aparece no tema cobalto)
def glitch():
    larg = [120, 96, 72, 48, 24, 108, 60]
    r = "".join(f'<rect x="{120 - larg[i % 7] * (0.5 if i % 5 == 0 else 1):.0f}" y="{i * 20}" '
                f'width="{larg[i % 7] * (0.5 if i % 5 == 0 else 1):.0f}" height="{6 if i % 3 else 12}"/>' for i in range(42))
    return f'<svg class="glitch" viewBox="0 0 120 840">{r}</svg>'

# ---------------------------------------------------------------- montagem
import graficos
MARCADORES = {**graficos.MARCADORES, "MAPA": mapa, "MAPA_ZOOM": mapa_zoom, "CONSTELACAO": constelacao, "CUBO": cubo, "GLITCH": glitch}

def expandir(html):
    def sub(m):
        nome, arg = m.group(1), m.group(2)
        if nome == "ICON":
            return icone(arg)
        if nome == "ESTRELA":
            return estrela(arg)
        return MARCADORES[nome]()
    return re.sub(r"\{\{(\w+)(?::([\w-]+))?\}\}", sub, html)

TEMAS = {
    "cobalto": ("Boletim cobalto",
                "https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;1,6..72,400&family=Hanken+Grotesk:wght@400;500;600&family=DM+Mono:wght@400;500&display=swap"),
}

base_vp = (AQUI / "viewport-base.css").read_text()
base = (AQUI / "base.css").read_text()
slides = expandir((AQUI / "slides.html").read_text())
js = (AQUI / "deck.js").read_text()

for tema, (_, fontes) in TEMAS.items():
    css = (AQUI / f"tema_{tema}.css").read_text()
    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Atenção Primária à Saúde em São Carlos – SCC0245</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="{fontes}" rel="stylesheet">
<style>
/* ======================= BASE 16:9 (viewport-base.css, obrigatório) ======================= */
{base_vp}
/* ======================= COMPONENTES COMUNS ======================= */
{base}
/* ======================= TEMA: {tema} (cores e fontes; edite as variáveis em :root) ======================= */
{css}
</style>
</head>
<body data-tema="{tema}">
<div class="deck-viewport">
<main class="deck-stage" id="deckStage">
{slides}
</main>
</div>
<div class="progress" id="progress"></div>
<aside class="notes" id="notes" aria-live="polite"></aside>
<div class="edit-hotzone"></div>
<button class="edit-toggle" id="editToggle" title="Modo de edição (E)">✎</button>
<script>
{js}
</script>
</body>
</html>
"""
    destino = SAIDA / f"apresentacao_{tema}.html"
    destino.write_text(html)
    print(f"ok: {destino.relative_to(SAIDA.parent)}  ({len(html) // 1024} KB)")
