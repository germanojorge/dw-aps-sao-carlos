import subprocess, math
D = {
 "dim_tempo": ["sk_tempo","ano_mes","mes","nome_mes","trimestre","semestre","ano"],
 "dim_localidade": ["sk_localidade","cod_municipio","municipio","regiao_imediata","regiao_intermediaria","uf"],
 "dim_estabelecimento": ["sk_estabelecimento","cnes","nome","tipo_unidade_cod","tipo_unidade","nivel_atencao","gestao","bairro","latitude","longitude","cod_municipio","municipio","regiao_imediata","uf"],
 "dim_tipo_equipe": ["sk_tipo_equipe","tipo_equipe_cod","tipo_equipe","categoria_equipe"],
 "dim_procedimento": ["sk_procedimento","cod_procedimento","forma_organizacao_cod","subgrupo_cod","grupo_cod","grupo"],
 "dim_diagnostico": ["sk_diagnostico","cid","cid_categoria","capitulo_num","capitulo","icsap","grupo_icsap"],
 "dim_perfil_paciente": ["sk_perfil","sexo","sexo_desc","faixa_etaria","ciclo_vida"],
 "dim_cbo": ["sk_cbo","cbo","familia_cbo","categoria_profissional"],
 "dim_junk_internacao": ["sk_junk","carater_atendimento","obito","uti"],
}
F = {
 "fato_equipe": (["sk_tempo","sk_estabelecimento","sk_tipo_equipe"], ["id_equipe"], [], "fato sem fato · grão: equipe ativa × mês"),
 "fato_internacao": (["sk_tempo","sk_estabelecimento","sk_procedimento","sk_diagnostico","sk_perfil","sk_localidade_residencia","sk_junk"], ["n_aih"], ["qtd_internacoes","dias_permanencia","valor_total"], "grão: uma internação (AIH)"),
 "fato_producao_ambulatorial": (["sk_tempo","sk_estabelecimento","sk_procedimento","sk_perfil","sk_localidade_residencia","sk_cbo"], [], ["qtd_apresentada","qtd_aprovada","valor_apresentado","valor_aprovado"], "grão: estab. × proced. × mês × perfil × residência × CBO"),
}
FK2DIM = {"sk_localidade_residencia":"dim_localidade","sk_perfil":"dim_perfil_paciente","sk_junk":"dim_junk_internacao"}
def dim_of(fk): return FK2DIM.get(fk, "dim_"+fk[3:])

def row(tag, name, bg="white", port=None):
    t = f'<FONT POINT-SIZE="9" COLOR="#555555">{tag}</FONT>  ' if tag else '<FONT POINT-SIZE="9" COLOR="white">XX</FONT>  '
    return f'<TR><TD ALIGN="LEFT" BGCOLOR="{bg}">{t}{name}</TD></TR>'
def dim_node(n):
    rows = [row("PK", f"<B>{D[n][0]}</B>", "#eef3fb")] + [row("", a) for a in D[n][1:]]
    return f'"{n}" [label=<<TABLE BORDER="1" CELLBORDER="0" CELLSPACING="0" CELLPADDING="3" COLOR="#2f5597"><TR><TD BGCOLOR="#2f5597"><FONT COLOR="white"><B>{n}</B></FONT></TD></TR>{"".join(rows)}</TABLE>>];'
def fact_node(n):
    fks, dds, ms, note = F[n]
    rows = [row("FK", k, "#fff4e5") for k in fks] + [row("DD", d, "#f3f3f3") for d in dds] + [row("M", m, "white") for m in ms]
    if not ms: rows.append(row("", "<I>(sem medidas: COUNT)</I>"))
    inner = f'<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0" CELLPADDING="3">{"".join(rows)}</TABLE>'
    return (f'"{n}" [label=<<TABLE BORDER="2" CELLBORDER="0" CELLSPACING="0" CELLPADDING="0" COLOR="#c55a11">'
            f'<TR><TD BGCOLOR="#c55a11" CELLPADDING="3"><FONT COLOR="white"><B>{n}</B></FONT></TD></TR>'
            f'<TR><TD CELLPADDING="3"><FONT POINT-SIZE="9"><I>{note}</I></FONT></TD></TR>'
            f'<TR><TD ALIGN="LEFT">{inner}</TD></TR></TABLE>>];')

HEAD = 'graph G { graph [fontname="DejaVu Sans", bgcolor="white", overlap=false, splines=true, sep="+18"]; node [shape=plaintext, fontname="DejaVu Sans", fontsize=11]; edge [color="#555555", penwidth=1.3, fontname="DejaVu Sans"];'
def render(name, body, engine):
    open(f"{name}.dot","w").write(HEAD + body + "}")
    for fmt in ("png","svg"):
        args = [engine, f"-T{fmt}", f"{name}.dot", "-o", f"{name}.{fmt}"]
        if fmt=="png": args.insert(1,"-Gdpi=180")
        subprocess.run(args, check=True)

def estrela(fname, fato, title):
    fks = F[fato][0]; dims = [dim_of(k) for k in fks]
    body = f'label=<<B>{title}</B>>; labelloc=t; fontsize=16; root="{fato}"; ranksep=2.2;' + fact_node(fato)
    for d in dims: body += dim_node(d)
    for k, d in zip(fks, dims):
        lab = ' [label="residência", fontsize=9]' if k=="sk_localidade_residencia" else ""
        body += f'"{fato}" -- "{d}"{lab};'
    render(fname, body, "twopi")

estrela("estrela_1_equipe", "fato_equipe", "Esquema estrela 1 – Oferta de equipes da APS (CNES)")
estrela("estrela_2_internacao", "fato_internacao", "Esquema estrela 2 – Internações hospitalares (SIH-SUS)")
estrela("estrela_3_producao", "fato_producao_ambulatorial", "Esquema estrela 3 – Produção ambulatorial (SIA-SUS)")

body = 'label=<<B>Constelação de fatos – Atenção básica em São Carlos</B><BR/><FONT POINT-SIZE="10">dimensões compartilhadas (conformes) com borda grossa</FONT>>; labelloc=t; fontsize=16; K=2.2;'
shared = {"dim_tempo","dim_estabelecimento","dim_procedimento","dim_perfil_paciente","dim_localidade"}
for f in F: body += fact_node(f)
alld = sorted({dim_of(k) for f in F for k in F[f][0]})
for d in alld:
    node = dim_node(d)
    if d in shared: node = node.replace('COLOR="#2f5597"><TR>','COLOR="#1f3864"><TR>').replace('BORDER="1"','BORDER="3"',1)
    body += node
for f in F:
    for k in F[f][0]:
        body += f'"{f}" -- "{dim_of(k)}";'
render("constelacao", body, "fdp")
