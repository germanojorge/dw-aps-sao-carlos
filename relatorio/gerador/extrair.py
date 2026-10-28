# Extrai o conteúdo do relatório (definido em conteudo.py) para conteudo.json,
# que o gerar.js monta em .docx. Rode de dentro desta pasta: python extrair.py
import json, re, html, os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

conteudo = open("conteudo.py", encoding="utf-8").read()


def runs(txt):
    """Converte a marcação simples do reportlab (<b>, <i>, <font name='Mono'>) em runs."""
    out, b, i, m = [], 0, 0, 0
    for tok in re.split(r"(<[^>]+>)", txt):
        if not tok:
            continue
        t = tok.lower()
        if t == "<b>": b += 1
        elif t == "</b>": b -= 1
        elif t == "<i>": i += 1
        elif t == "</i>": i -= 1
        elif t.startswith("<font"): m += 1
        elif t == "</font>": m -= 1
        elif t.startswith("<"): pass
        else:
            out.append({"t": html.unescape(tok), "b": b > 0, "i": i > 0, "m": m > 0})
    return out


class Style:
    def __init__(self, name, parent=None, **kw):
        self.name = name


BODY, BUL, H1, H2, H3 = Style("body"), Style("bul"), Style("H1"), Style("H2"), Style("H3")
CAP, HIER = Style("cap"), Style("hier")
S = []


def Paragraph(text, style, bulletText=None):
    kind = {"body": "p", "bul": "bullet", "H1": "h1", "H2": "h2", "H3": "h3", "cap": "caption",
            "hier": "hier", "hd": "pbold"}.get(style.name, "p")
    if bulletText:
        kind = "bullet"
    return {"k": kind, "r": runs(text)}


def KeepTogether(x):
    return {"k": "group", "items": x if isinstance(x, list) else [x]}


def PageBreak():
    return {"k": "pagebreak"}


def p(t, st=BODY): S.append(Paragraph(t, st))
def h1(t): S.append(Paragraph(t, H1))
def h2(t): S.append(Paragraph(t, H2))
def h3(t): S.append(Paragraph(t, H3))
def bullets(items):
    for it in items:
        S.append(Paragraph(it, BUL, bulletText="•"))
def hier(*linhas):
    for l in linhas:
        S.append({"k": "hier", "r": runs(l)})


def tabela(cab, linhas, larg, keep=False):
    S.append({"k": "table", "head": [runs(c) for c in cab],
              "rows": [[runs(str(c)) for c in l] for l in linhas], "w": larg, "keep": keep})


def figura(path, legenda, max_w=16, max_h=21, titulo=None):
    if titulo:
        S.append(Paragraph(titulo, H2))
    S.append({"k": "img", "path": path, "max_h": max_h})
    S.append(Paragraph(legenda, CAP))


class _cm(float):
    pass
ns = dict(globals())
from PIL import Image as PI
ROT = "constelacao_rot.png"
PI.open("../../esquemas/constelacao.png").rotate(90, expand=True).save(ROT)
ns.update(cm=1.0, IMG="../../esquemas/", ParagraphStyle=Style, ROT=ROT)
exec(conteudo, ns)


def achatar(lst):
    for x in lst:
        if isinstance(x, dict) and x.get("k") == "group":
            yield from achatar(x["items"])
        else:
            yield x


blocos = list(achatar(ns["S"]))
json.dump(blocos, open("conteudo.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(blocos), "blocos;", {k: sum(1 for b in blocos if b["k"] == k) for k in {b["k"] for b in blocos}})
