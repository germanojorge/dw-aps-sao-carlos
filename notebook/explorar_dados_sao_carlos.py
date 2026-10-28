"""
Exploração inicial dos dados do DATASUS para São Carlos (SP).
Uso:
    pip install pysus pandas
    python explorar_dados_sao_carlos.py
Gera o arquivo relatorio_exploracao.txt (é esse que vocês me mandam de volta).
Baixa só 1 mês de cada base, para ser rápido. Os arquivos do SIA de SP são
grandes; se a memória apertar, rode uma base por vez comentando as outras.
"""
import pandas as pd
import pysus

MUN = "354890"          # São Carlos, código IBGE de 6 dígitos (padrão DATASUS)
ANO, MES = 2024, 6
SAIDA = open("relatorio_exploracao.txt", "w", encoding="utf-8")


def log(*a):
    print(*a)
    print(*a, file=SAIDA)


def baixar(func, **kw):
    """Compatível com as duas versões da API do PySUS."""
    try:
        r = func(state="SP", year=ANO, month=MES, as_dataframe=True, **kw)
    except TypeError:
        r = func(state="SP", year=ANO, month=MES, **kw)
    if isinstance(r, list):  # versões que devolvem caminhos de parquet
        r = pd.concat([pd.read_parquet(p) for p in r], ignore_index=True)
    return r


def filtrar_mun(df, colunas):
    for c in colunas:
        if c in df.columns:
            return df[df[c].astype(str).str[:6] == MUN], c
    return df, None


def resumir(nome, df, col_mun, colunas_chave):
    log("\n" + "=" * 70)
    log(f"{nome} | filtro por {col_mun} | {len(df)} linhas em São Carlos")
    log("Colunas:", list(df.columns))
    for c in colunas_chave:
        if c in df.columns:
            log(f"\n-- {c} (top 10) --")
            log(df[c].value_counts(dropna=False).head(10).to_string())
    log("\nAmostra:")
    log(df.head(5).to_string())


log(f"PySUS {getattr(pysus, '__version__', '?')} | competência {MES:02d}/{ANO}")

bases = [
    ("CNES - Estabelecimentos (ST)", pysus.cnes, {"group": "ST"},
     ["CODUFMUN"], ["TP_UNID", "TPGESTAO", "NIV_DEP"]),
    ("CNES - Equipes (EP)", pysus.cnes, {"group": "EP"},
     ["CODUFMUN"], ["TIPO_EQP", "CNES"]),
    ("CNES - Profissionais (PF)", pysus.cnes, {"group": "PF"},
     ["CODUFMUN"], ["CBO", "TERCEIRO"]),
    ("SIH - Internações (RD)", pysus.sih, {"group": "RD"},
     ["MUNIC_RES", "MUNIC_MOV"], ["SEXO", "COD_IDADE", "DIAG_PRINC", "CNES", "MORTE"]),
    ("SIA - Produção ambulatorial (PA)", pysus.sia, {"group": "PA"},
     ["PA_UFMUN", "PA_MUNPCN"], ["PA_SEXO", "PA_PROC_ID", "PA_CODUNI", "PA_CBOCOD"]),
]

for nome, func, kw, cols_mun, chave in bases:
    try:
        df = baixar(func, **kw)
        log(f"\n{nome}: {len(df)} linhas no estado de SP")
        df_sc, col = filtrar_mun(df, cols_mun)
        resumir(nome, df_sc, col, chave)
    except Exception as e:
        log(f"\n{nome}: ERRO -> {type(e).__name__}: {e}")

SAIDA.close()
