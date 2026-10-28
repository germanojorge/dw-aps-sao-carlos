"""
Roda as 5 consultas OLAP no DW e salva os resultados em dados/consultas.json,
que o build.py usa para desenhar os gráficos dos slides.

Uso (de dentro de apresentacao/gerador/, com o venv do notebook):
    ../../notebook/.venv/bin/python exportar_consultas.py

As consultas são as mesmas do notebook (seção 7), com os mesmos filtros:
demanda filtra pela residência = São Carlos; oferta pelo município do estabelecimento.
"""
import json
from pathlib import Path
import duckdb

AQUI = Path(__file__).parent
DB = AQUI.parent.parent / "notebook" / "dados" / "dw_aps_sao_carlos.duckdb"
SIGTAP = json.loads((AQUI / "dados" / "sigtap_202412.json").read_text())
MUN, POP = "354890", 254_857

con = duckdb.connect(str(DB), read_only=True)
def q(sql):
    return [dict(zip([d[0] for d in con.description], r)) for r in con.execute(sql).fetchall()]

RES = f"JOIN dim_localidade l ON l.sk_localidade = f.sk_localidade_residencia AND l.cod_municipio = '{MUN}'"
ICSAP = "JOIN dim_diagnostico d USING (sk_diagnostico)"

# ---------- Q1 roll-up: ICSAP de residentes por mês, trimestre e ano
q1_mes = q(f"""SELECT t.ano_mes, t.trimestre, t.ano, SUM(f.qtd_internacoes)::INT AS n
    FROM fato_internacao f JOIN dim_tempo t USING (sk_tempo) {ICSAP} {RES}
    WHERE d.icsap = 'Sim' GROUP BY ALL ORDER BY t.ano_mes""")
q1_tri = q(f"""SELECT t.trimestre, SUM(f.qtd_internacoes)::INT AS n
    FROM fato_internacao f JOIN dim_tempo t USING (sk_tempo) {ICSAP} {RES}
    WHERE d.icsap = 'Sim' GROUP BY 1 ORDER BY 1""")
q1_ano = q(f"""SELECT t.ano, SUM(f.qtd_internacoes)::INT AS n
    FROM fato_internacao f JOIN dim_tempo t USING (sk_tempo) {ICSAP} {RES}
    WHERE d.icsap = 'Sim' GROUP BY 1 ORDER BY 1""")

# ---------- Q2 drill-down: produção aprovada em estabelecimentos de São Carlos
EST = f"JOIN dim_estabelecimento e USING (sk_estabelecimento) JOIN dim_procedimento p USING (sk_procedimento) WHERE e.cod_municipio = '{MUN}'"
q2_grupo = q(f"""SELECT p.grupo_cod AS cod, SUM(f.qtd_aprovada)::BIGINT AS n, SUM(f.valor_aprovado)::DOUBLE AS valor
    FROM fato_producao_ambulatorial f {EST} GROUP BY 1 ORDER BY 2 DESC""")
g = q2_grupo[0]["cod"]
q2_sub = q(f"""SELECT p.subgrupo_cod AS cod, SUM(f.qtd_aprovada)::BIGINT AS n
    FROM fato_producao_ambulatorial f {EST} AND p.grupo_cod = '{g}' GROUP BY 1 ORDER BY 2 DESC""")
sg = q2_sub[0]["cod"]
q2_proc = q(f"""SELECT p.cod_procedimento AS cod, SUM(f.qtd_aprovada)::BIGINT AS n
    FROM fato_producao_ambulatorial f {EST} AND p.subgrupo_cod = '{sg}' GROUP BY 1 ORDER BY 2 DESC LIMIT 6""")
for r in q2_grupo: r["nome"] = SIGTAP["grupo"].get(r["cod"], "Não informado")
for r in q2_sub: r["nome"] = SIGTAP["subgrupo"].get(r["cod"], r["cod"])
for r in q2_proc: r["nome"] = SIGTAP["procedimento"].get(r["cod"], r["cod"]).capitalize()

# ---------- Q3 slice and dice: ICSAP de idosos residentes em 2024, por causa e sexo
q3 = q(f"""SELECT d.grupo_icsap AS causa, pp.sexo, SUM(f.qtd_internacoes)::INT AS n,
           SUM(f.dias_permanencia)::INT AS dias
    FROM fato_internacao f JOIN dim_tempo t USING (sk_tempo) {ICSAP}
    JOIN dim_perfil_paciente pp USING (sk_perfil) {RES}
    WHERE t.ano = 2024 AND pp.ciclo_vida = 'Idoso' AND d.icsap = 'Sim' AND pp.sexo IN ('F', 'M')
    GROUP BY ALL""")

# ---------- Q4 pivot: ICSAP de residentes por causa × ciclo de vida (período todo)
q4 = q(f"""SELECT d.grupo_icsap AS causa, pp.ciclo_vida AS ciclo, SUM(f.qtd_internacoes)::INT AS n
    FROM fato_internacao f {ICSAP} JOIN dim_perfil_paciente pp USING (sk_perfil) {RES}
    WHERE d.icsap = 'Sim' AND pp.ciclo_vida IN ('Criança', 'Adolescente', 'Adulto', 'Idoso')
    GROUP BY ALL""")

# ---------- Q5 drill-across: cada fato agregado por mês e depois juntado por ano_mes
q5 = q(f"""
WITH oferta AS (
    SELECT f.sk_tempo, COUNT(*) AS equipes_sf
    FROM fato_equipe f JOIN dim_tipo_equipe te USING (sk_tipo_equipe)
    JOIN dim_estabelecimento e USING (sk_estabelecimento)
    WHERE te.categoria_equipe = 'Saúde da Família' AND e.cod_municipio = '{MUN}' GROUP BY 1),
producao AS (
    SELECT f.sk_tempo, SUM(f.qtd_aprovada) AS producao_aps
    FROM fato_producao_ambulatorial f JOIN dim_estabelecimento e USING (sk_estabelecimento)
    WHERE e.nivel_atencao = 'Atenção Primária' AND e.cod_municipio = '{MUN}' GROUP BY 1),
icsap AS (
    SELECT f.sk_tempo, SUM(f.qtd_internacoes) AS internacoes_icsap
    FROM fato_internacao f {ICSAP} {RES} WHERE d.icsap = 'Sim' GROUP BY 1)
SELECT t.ano_mes,
       COALESCE(o.equipes_sf, 0)::INT AS equipes_sf,
       ROUND(LEAST(100, 100.0 * COALESCE(o.equipes_sf, 0) * 3450 / {POP}), 1)::DOUBLE AS cobertura,
       COALESCE(p.producao_aps, 0)::BIGINT AS producao_aps,
       COALESCE(i.internacoes_icsap, 0)::INT AS icsap,
       ROUND(10000.0 * COALESCE(i.internacoes_icsap, 0) / {POP}, 2)::DOUBLE AS taxa
FROM dim_tempo t LEFT JOIN oferta o USING (sk_tempo) LEFT JOIN producao p USING (sk_tempo)
LEFT JOIN icsap i USING (sk_tempo)
WHERE t.sk_tempo > 0 ORDER BY 1""")

# ---------- números de apoio (conferência)
apoio = q(f"""SELECT
    (SELECT SUM(qtd_internacoes) FROM fato_internacao f {RES})::INT AS internacoes_residentes,
    (SELECT SUM(qtd_internacoes) FROM fato_internacao f {ICSAP} {RES} WHERE d.icsap = 'Sim')::INT AS icsap_residentes""")[0]

saida = {"q1": {"mes": q1_mes, "tri": q1_tri, "ano": q1_ano},
         "q2": {"grupo": q2_grupo, "sub": q2_sub, "proc": q2_proc, "grupo_escolhido": g, "sub_escolhido": sg},
         "q3": q3, "q4": q4, "q5": q5, "apoio": apoio}
(AQUI / "dados" / "consultas.json").write_text(json.dumps(saida, ensure_ascii=False, indent=1, default=str))
print("ok:", {k: (len(v) if isinstance(v, list) else "…") for k, v in saida.items()}, apoio)
