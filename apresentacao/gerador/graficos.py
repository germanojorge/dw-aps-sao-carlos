"""
Gráficos SVG das 5 consultas OLAP, a partir de dados/consultas.json (gerado por exportar_consultas.py).
As cores vêm das variáveis CSS do tema (--acc, --hit-bg, --ink, --mute, --faint), então o mesmo SVG
serve aos dois estilos. Regras seguidas: um eixo por gráfico (Q5 usa painéis empilhados, não eixo duplo),
uma cor só por gráfico (série única), rótulos seletivos e <title> em cada marca (tooltip ao passar o mouse).
"""
import json
from pathlib import Path
from xml.sax.saxutils import escape

DADOS = json.loads((Path(__file__).parent / "dados" / "consultas.json").read_text())
MESES = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]

CURTO = {  # rótulos curtos dos grupos de ICSAP para eixos apertados
    "01": "Imunopreveníveis", "02": "Gastroenterites", "03": "Anemia", "04": "Def. nutricionais",
    "05": "Ouvido/nariz/garganta", "06": "Pneumonias bact.", "07": "Asma", "08": "D. pulmonares",
    "09": "Hipertensão", "10": "Angina", "11": "Insuf. cardíaca", "12": "Cerebrovasculares",
    "13": "Diabetes", "14": "Epilepsias", "15": "Rim e trato urinário", "16": "Pele e subcutâneo",
    "17": "Inflam. pélvica fem.", "18": "Úlcera GI", "19": "Pré-natal e parto",
}
def curto(causa): return CURTO.get(causa[:2], causa)

def fmt(v, dec=0):
    s = f"{v:,.{dec}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")

def fmt_compacto(v):
    if v >= 1e6: return fmt(v / 1e6, 1) + " mi"
    if v >= 1e4: return fmt(v / 1e3, 0) + " mil"
    return fmt(v)

def barra_v(x, base, w, h, cls="ch-bar", tip=""):
    """barra vertical com topo arredondado (4px) e base reta"""
    h = max(h, 0.0)
    r = min(4, w / 2, h)
    d = (f"M{x:.1f},{base:.1f} V{base - h + r:.1f} Q{x:.1f},{base - h:.1f} {x + r:.1f},{base - h:.1f} "
         f"H{x + w - r:.1f} Q{x + w:.1f},{base - h:.1f} {x + w:.1f},{base - h + r:.1f} V{base:.1f} Z")
    return f'<path class="{cls}" d="{d}"><title>{escape(tip)}</title></path>'

def barra_h(x, y, w, h, cls="ch-bar", tip=""):
    """barra horizontal com ponta arredondada (4px) e início reto"""
    w = max(w, 0.0)
    r = min(4, h / 2, w)
    d = (f"M{x:.1f},{y:.1f} H{x + w - r:.1f} Q{x + w:.1f},{y:.1f} {x + w:.1f},{y + r:.1f} "
         f"V{y + h - r:.1f} Q{x + w:.1f},{y + h:.1f} {x + w - r:.1f},{y + h:.1f} H{x:.1f} Z")
    return f'<path class="{cls}" d="{d}"><title>{escape(tip)}</title></path>'

def txt(x, y, s, cls="ch-t", anchor="start", extra=""):
    return f'<text class="{cls}" x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" {extra}>{escape(str(s))}</text>'

# ===================================================================== Q1 roll-up
def q1():
    W = 1680
    meses, tris, anos = DADOS["q1"]["mes"], DADOS["q1"]["tri"], DADOS["q1"]["ano"]
    gap = 8
    s, y0 = "", 0
    linhas = [("ano_mes", meses, 150, lambda r: f'{MESES[int(str(r["ano_mes"])[4:]) - 1]} {str(r["ano_mes"])[:4]}'),
              ("trimestre", tris, 140, lambda r: r["trimestre"]),
              ("ano", anos, 110, lambda r: str(r["ano"]))]
    for nivel, rows, H, nome in linhas:
        n = len(rows)
        bw = (W - gap * (n - 1)) / n
        vmax = max(r["n"] for r in rows) or 1
        base = y0 + 34 + H
        s += txt(0, y0 + 18, nivel, "ch-lv")
        s += f'<line class="ch-base" x1="0" x2="{W}" y1="{base}" y2="{base}"/>'
        ordem = sorted(range(n), key=lambda i: rows[i]["n"])
        mostrar = set(range(n)) if n <= 8 else {ordem[0], ordem[-1]}   # meses: só mínimo e máximo
        for i, r in enumerate(rows):
            x = i * (bw + gap)
            h = H * r["n"] / vmax
            cls = "ch-bar" + (" hl" if nivel == "ano" else "")
            s += barra_v(x, base, bw, h, cls, f"{nome(r)}: {fmt(r['n'])} internações ICSAP")
            if i in mostrar:
                s += txt(x + bw / 2, base - h - 10, fmt(r["n"]), "ch-v", "middle")
            if nivel == "ano_mes":
                if int(str(r["ano_mes"])[4:]) in (1, 7):
                    s += txt(x, base + 26, nome(r), "ch-x")
            else:
                s += txt(x + bw / 2, base + 28, nome(r), "ch-x", "middle")
        y0 = base + 60
    return f'<svg class="graf q1g" viewBox="0 -4 {W} {y0}">{s}</svg>'

# ===================================================================== Q2 drill-down
def coluna_barras(rows, escolhido, W, titulo, max_rows, rotulo, cod=True):
    rows = rows[:max_rows]
    vmax = max(r["n"] for r in rows) or 1
    s = txt(0, 20, titulo, "ch-lv")
    y = 50
    for r in rows:
        hl = r["cod"] == escolhido
        nome = (f'{r["cod"]} · ' if cod else "") + rotulo(r)
        if len(nome) > 44: nome = nome[:42] + "…"
        s += txt(0, y + 20, nome, "ch-cat" + (" on" if hl else ""))
        w = (W - 110) * r["n"] / vmax
        s += barra_h(0, y + 32, w, 18, "ch-bar" + (" hl" if hl else " dim"), f'{r["cod"]} {rotulo(r)}: {fmt(r["n"])} aprovados')
        s += txt(w + 10, y + 47, fmt_compacto(r["n"]), "ch-v")
        y += 74
    return s, y

def q2():
    d = DADOS["q2"]
    W1, W2, W3, G = 540, 480, 560, 50
    s1, h1 = coluna_barras(d["grupo"], d["grupo_escolhido"], W1, "grupo", 8, lambda r: r["nome"])
    s2, h2 = coluna_barras(d["sub"], d["sub_escolhido"], W2, f'subgrupo de {d["grupo_escolhido"]}', 7, lambda r: r["nome"])
    s3, h3 = coluna_barras(d["proc"], None, W3, f'procedimento de {d["sub_escolhido"]}', 6, lambda r: r["nome"], cod=False)
    H = max(h1, h2, h3)
    x2, x3 = W1 + G, W1 + G + W2 + G
    seta = lambda x: f'<path class="ch-arrow" d="M{x - G + 10},{H / 2} h{G - 26} m-10,-8 l10,8 l-10,8"/>'
    return (f'<svg class="graf q2g" viewBox="0 0 {x3 + W3} {H}">{s1}'
            f'<g transform="translate({x2},0)">{s2}</g><g transform="translate({x3},0)">{s3}</g>'
            f'{seta(x2)}{seta(x3)}</svg>')

# ===================================================================== Q3 slice and dice
def q3():
    rows = DADOS["q3"]
    tot = {}
    for r in rows: tot[r["causa"]] = tot.get(r["causa"], 0) + r["n"]
    causas = sorted(tot, key=lambda c: -tot[c])[:8]
    val = {(r["causa"], r["sexo"]): r for r in rows}
    vmax = max(r["n"] for r in rows) or 1
    LBL, COL, DIAS = 330, 290, 150
    s = txt(LBL, 22, "feminino", "ch-lv") + txt(LBL + COL + 20, 22, "masculino", "ch-lv")
    s += txt(LBL + 2 * COL + 40 + DIAS, 22, "média de dias", "ch-lv", "end")
    y = 46
    for c in causas:
        s += txt(0, y + 30, curto(c), "ch-cat")
        dias_t = n_t = 0
        for j, sexo in enumerate(("F", "M")):
            r = val.get((c, sexo), {"n": 0, "dias": 0})
            x = LBL + j * (COL + 20)
            w = (COL - 70) * r["n"] / vmax
            s += barra_h(x, y + 12, w, 26, "ch-bar", f'{curto(c)}, {"feminino" if sexo == "F" else "masculino"}: {r["n"]} internações')
            s += txt(x + w + 10, y + 32, fmt(r["n"]), "ch-v")
            dias_t += r["dias"]; n_t += r["n"]
        s += txt(LBL + 2 * COL + 40 + DIAS, y + 32, fmt(dias_t / n_t, 1) if n_t else "–", "ch-v strong", "end")
        y += 64
    total = sum(r["n"] for r in rows)
    s += f'<line class="ch-base" x1="0" x2="{LBL + 2 * COL + 40 + DIAS}" y1="{y + 4}" y2="{y + 4}"/>'
    s += txt(0, y + 40, f"total: {fmt(total)} internações ICSAP de idosos em 2024", "ch-x")
    return f'<svg class="graf q3g" viewBox="0 0 {LBL + 2 * COL + 40 + DIAS} {y + 50}">{s}</svg>'

# ===================================================================== Q4 pivot (mapa de calor)
CICLOS = ["Criança", "Adolescente", "Adulto", "Idoso"]

def heat(linhas, colunas, valor, LBL, CW, CH, rot):
    vmax = max(valor(l, c) for l in linhas for c in colunas) or 1
    top = 170 if rot else 44
    s = ""
    for j, c in enumerate(colunas):
        cx = LBL + j * CW + CW / 2
        if rot:
            s += txt(cx - 4, top - 12, c, "ch-x", "start", f'transform="rotate(-60 {cx - 4} {top - 12})"')
        else:
            s += txt(cx, top - 14, c, "ch-x", "middle")
    for i, l in enumerate(linhas):
        y = top + i * CH
        s += txt(0, y + CH / 2 + 8, l, "ch-cat")
        for j, c in enumerate(colunas):
            v = valor(l, c)
            a = 0.08 + 0.92 * (v / vmax) ** 0.8          # rampa sequencial de um tom: claro → escuro
            x = LBL + j * CW
            s += (f'<rect class="ch-cell" x="{x + 1}" y="{y + 1}" width="{CW - 2}" height="{CH - 2}" rx="4" '
                  f'style="fill-opacity:{a:.2f}"><title>{escape(f"{l} × {c}: {v}")}</title></rect>')
            s += txt(x + CW / 2, y + CH / 2 + 8, fmt(v), "ch-cv" + (" inv" if a > 0.55 else ""), "middle")
    return s, LBL + len(colunas) * CW, top + len(linhas) * CH

def q4():
    rows = DADOS["q4"]
    tot = {}
    for r in rows: tot[r["causa"]] = tot.get(r["causa"], 0) + r["n"]
    causas = sorted(tot, key=lambda c: -tot[c])[:7]
    v = {(r["causa"], r["ciclo"]): r["n"] for r in rows}
    nomes = {curto(c): c for c in causas}
    rotulo = {"Criança": "criança", "Adolescente": "adolesc.", "Adulto": "adulto", "Idoso": "idoso"}
    ciclo = {rotulo[c]: c for c in CICLOS}
    sa, wa, ha = heat([curto(c) for c in causas], list(rotulo.values()),
                      lambda l, c: v.get((nomes[l], ciclo[c]), 0), 270, 116, 64, False)
    sb, wb, hb = heat(CICLOS, [curto(c) for c in causas], lambda l, c: v.get((nomes[c], l), 0), 180, 92, 64, True)
    gap = 110
    H = max(ha, hb)
    seta = f'<text class="ch-rot" x="{wa + gap / 2}" y="{H / 2 + 30}" text-anchor="middle">↻</text>'
    return (f'<svg class="graf q4g" viewBox="0 0 {wa + gap + wb} {H}">{sa}{seta}'
            f'<g transform="translate({wa + gap},{H - hb})">{sb}</g></svg>')

# ===================================================================== Q5 drill-across (painéis empilhados, eixo x comum)
def q5():
    rows = DADOS["q5"]
    W, LBL, PH, GAP = 1680, 360, 240, 56
    pct = lambda v: fmt(v, 1) + "%"
    # cada painel: (título, subtítulo, séries [(campo, rótulo)], formato); várias séries dividem o mesmo eixo
    paineis = [
        ("cobertura estimada", "fato_equipe · COUNT", [("cobertura_ab", "eSF + eAP"), ("cobertura", "só eSF")], pct),
        ("ICSAP / 10 mil hab.", "fato_internacao · Σ ICSAP", [("taxa", None)], lambda v: fmt(v, 2)),
    ]
    n = len(rows)
    xw = W - LBL - 300     # espaço à direita para os rótulos das séries
    X = lambda i: LBL + i * xw / (n - 1)
    s, y0 = "", 0
    for titulo, sub, series, f in paineis:
        s += txt(0, y0 + 40, titulo, "ch-pt") + txt(0, y0 + 72, sub, "ch-x")
        todos = [r[c] for c, _ in series for r in rows]
        lo, hi = min(todos), max(todos)
        pad = (hi - lo) * 0.2 or 1
        lo, hi = max(0, lo - pad), hi + pad
        Y = lambda v: y0 + PH - (v - lo) / (hi - lo) * PH
        s += f'<line class="ch-grid" x1="{LBL}" x2="{LBL + xw}" y1="{y0 + PH}" y2="{y0 + PH}"/>'
        for k, (campo, rotulo) in enumerate(series):
            vals = [r[campo] for r in rows]
            alt = " alt" if k else ""
            pts = " ".join(f"{X(i):.1f},{Y(v):.1f}" for i, v in enumerate(vals))
            s += f'<polyline class="ch-line{alt}" points="{pts}"/>'
            for i, (r, v) in enumerate(zip(rows, vals)):
                s += (f'<circle class="ch-dot{alt}" cx="{X(i):.1f}" cy="{Y(v):.1f}" r="5">'
                      f'<title>{escape(f"{r["ano_mes"]}: {f(v)}")}</title></circle>')
            if rotulo:
                # série com nome: só o último valor, com o rótulo ao lado
                s += txt(X(n - 1) + 14, Y(vals[-1]) + 8, f"{f(vals[-1])} {rotulo}", "ch-v")
                continue
            imin, imax = vals.index(min(vals)), vals.index(max(vals))
            marcar = {n - 1} if min(vals) == max(vals) else {imin, imax, n - 1}
            for i in marcar:
                lado = i == n - 1 or (i == imin and i != imax)     # último e mínimo: rótulo ao lado do ponto
                s += txt(X(i) + (14 if lado else 0), Y(vals[i]) + (8 if i == imin and i != n - 1 else -14), f(vals[i]), "ch-v",
                         "start" if lado else "middle")
        y0 += PH + GAP
    for i, r in enumerate(rows):
        m = int(str(r["ano_mes"])[4:])
        if m in (1, 4, 7, 10):
            s += txt(X(i), y0 - GAP + 30, f'{MESES[m - 1]}/{str(r["ano_mes"])[2:4]}', "ch-x", "middle")
    s += (f'<text class="ch-join" x="{W - 24}" y="{y0 / 2}" text-anchor="middle" '
          f'transform="rotate(90 {W - 24} {y0 / 2})">⋈ ano_mes</text>')
    return f'<svg class="graf q5g" viewBox="0 0 {W} {y0}">{s}</svg>'

# ===================================================================== slide 4: rede de atenção primária (1 quadrado = 1 unidade)
def rede():
    rows = DADOS["rede"]
    COLS, C, G = 6, 92, 16
    LEG = [("usf", "USF", "uma equipe de Saúde da Família (eSF) cada"),
           ("ubs", "UBS tradicionais", "uma equipe de Atenção Primária (eAP) cada"),
           ("sem", "sem eSF nem eAP", "")]
    s = ""
    for i, r in enumerate(rows):
        x, y = (i % COLS) * (C + G), (i // COLS) * (C + G)
        s += (f'<rect class="rd {r["modelo"]}" x="{x}" y="{y}" width="{C}" height="{C}" rx="6" style="--i:{i}">'
              f'<title>{escape(r["nome"])}</title></rect>')
    lx, ly = COLS * (C + G) + 70, 40
    for k, (m, nome, desc) in enumerate(LEG):
        n = sum(r["modelo"] == m for r in rows)
        y = ly + k * 210
        s += f'<rect class="rd {m} leg" x="{lx}" y="{y}" width="44" height="44" rx="4"/>'
        s += txt(lx + 70, y + 40, f"{n} {nome}", "ch-pt")
        if desc:
            s += txt(lx + 70, y + 84, desc, "ch-x")
    W, H = lx + 560, (len(rows) + COLS - 1) // COLS * (C + G) - G
    return f'<svg class="graf rede" viewBox="0 0 {W} {H}">{s}</svg>'

MARCADORES = {"Q1": q1, "Q2": q2, "Q3": q3, "Q4": q4, "Q5": q5, "REDE": rede}
