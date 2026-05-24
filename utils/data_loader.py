import os
import sys
import sqlite3 as _sqlite3
import unicodedata as _ud

import pandas as pd
import geopandas as gpd
import streamlit as st

# ── garante que o root do projeto esteja no sys.path ────────────────────────
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from utils.processamento import carregar_sinan, agregar_por_municipio, top10, evolucao_total  # noqa: F401

# ── helpers internos ─────────────────────────────────────────────────────────
def _norm(s):
    if not isinstance(s, str):
        return ""
    s = _ud.normalize("NFKD", s)
    return s.encode("ascii", errors="ignore").decode("ascii").upper().strip()


def _to_int(v):
    try:
        return int(float(str(v).strip().replace("-", "0").replace(",", "") or "0"))
    except Exception:
        return 0


def _ler_regiao(caminho, col_linha, validos):
    df = pd.read_csv(caminho, sep=";", encoding="latin1", skiprows=4, header=0)
    df.columns = [col_linha, "bh_nucl", "bh_colar", "vale_nucl", "vale_colar",
                  "df_entorno", "fora_metro", "ignorado", "total"]
    df = df[df[col_linha].isin(validos)].copy()
    for c in ["bh_nucl", "bh_colar", "vale_nucl", "vale_colar", "df_entorno", "fora_metro", "total"]:
        df[c] = df[c].apply(_to_int)
    df["urbano"]    = df[["bh_nucl", "bh_colar", "vale_nucl", "vale_colar", "df_entorno"]].sum(axis=1)
    df["rural"]     = df["fora_metro"]
    df["pct_rural"] = (df["rural"] / (df["rural"] + df["urbano"]) * 100).round(1)
    return df.reset_index(drop=True)


def _ler_trabalho(caminho, col_linha, validos):
    df = pd.read_csv(caminho, sep=";", encoding="latin1", skiprows=4, header=0)
    df.columns = [col_linha, "ignorado", "sim", "nao", "total"]
    df = df[df[col_linha].isin(validos)].copy()
    for c in ["ignorado", "sim", "nao", "total"]:
        df[c] = df[c].apply(_to_int)
    df["pct_trabalho"] = (df["sim"] / df["total"] * 100).round(1)
    return df.reset_index(drop=True)


# ── funções de carregamento ───────────────────────────────────────────────────
@st.cache_data
def load_data():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    df = carregar_sinan(os.path.join(base, "data", "municipios_ano.csv"))
    geojson_path = os.path.join(base, "data", "mg_municipios.geojson")
    gdf = None
    if os.path.exists(geojson_path):
        gdf = gpd.read_file(geojson_path)[["NM_MUN", "geometry"]].copy()
        gdf["geometry"] = gdf["geometry"].simplify(0.001, preserve_topology=True)
        gdf["municipio"] = gdf["NM_MUN"].apply(_norm)
        gdf = gdf.drop(columns=["NM_MUN"])
        centroids = gdf.to_crs(epsg=31983).geometry.centroid.to_crs(epsg=4326)
        gdf["centroid_lat"] = centroids.y.round(6)
        gdf["centroid_lon"] = centroids.x.round(6)
    return df, gdf


@st.cache_data
def get_gdf_merged(anos_tuple, _df_raw, _gdf):
    df_agg_local = agregar_por_municipio(_df_raw, list(anos_tuple))
    merged = _gdf.merge(df_agg_local[["municipio", "total_acidentes"]], on="municipio", how="left")
    merged["total_acidentes"] = merged["total_acidentes"].fillna(0)
    geo_iface = merged.__geo_interface__
    return merged, df_agg_local, geo_iface


@st.cache_data
def load_animal_data():
    base = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
    TIPOS_VALIDOS     = ["Serpente", "Aranha", "Escorpião", "Lagarta", "Abelha", "Outros"]
    ESPECIES_SERPENTE = ["Botrópico", "Crotálico", "Elapídico", "Laquético", "Não Peçonhenta"]
    ESPECIES_ARANHA   = ["Foneutrismo", "Loxoscelismo", "Latrodectismo", "Outra aranha"]
    tipo_reg  = _ler_regiao(os.path.join(base, "tipo_regiao_metro.csv"),   "tipo",    TIPOS_VALIDOS)
    tipo_trab = _ler_trabalho(os.path.join(base, "tipo_trabalho.csv"),     "tipo",    TIPOS_VALIDOS)
    serp_trab = _ler_trabalho(os.path.join(base, "serpente_trabalho.csv"), "especie", ESPECIES_SERPENTE)
    aran_trab = _ler_trabalho(os.path.join(base, "aranha_trabalho.csv"),   "especie", ESPECIES_ARANHA)
    return tipo_reg, tipo_trab, serp_trab, aran_trab


def _db_path():
    return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "acidentes.db")


@st.cache_data
def load_sazonalidade():
    conn = _sqlite3.connect(_db_path())
    df = pd.read_sql_query("""
        SELECT o.ano, o.mes, t.descricao AS tipo_animal, COUNT(*) AS casos
        FROM ocorrencia o
        JOIN tipo_animal t ON o.id_tipo_animal = t.id_tipo_animal
        WHERE t.descricao != 'Ign/Branco'
        GROUP BY o.ano, o.mes, t.descricao
        ORDER BY o.ano, o.mes, t.descricao
    """, conn)
    conn.close()
    meses = {1:"Jan",2:"Fev",3:"Mar",4:"Abr",5:"Mai",6:"Jun",
             7:"Jul",8:"Ago",9:"Set",10:"Out",11:"Nov",12:"Dez"}
    df["mes_nome"] = df["mes"].map(meses)
    df["periodo"]  = df["ano"].astype(str) + "/" + df["mes"].apply(lambda m: f"{m:02d}")
    return df


@st.cache_data
def load_demografico():
    conn = _sqlite3.connect(_db_path())
    df = pd.read_sql_query("""
        SELECT o.sexo, o.raca, o.faixa_etaria, t.descricao AS tipo_animal, COUNT(*) AS casos
        FROM ocorrencia o
        JOIN tipo_animal t ON o.id_tipo_animal = t.id_tipo_animal
        WHERE o.sexo IS NOT NULL AND o.faixa_etaria IS NOT NULL
        GROUP BY o.sexo, o.raca, o.faixa_etaria, t.descricao
    """, conn)
    conn.close()
    return df


@st.cache_data
def load_desfecho():
    conn = _sqlite3.connect(_db_path())
    df = pd.read_sql_query("""
        SELECT o.soroterapia, g.descricao AS grau, e.descricao AS evolucao,
               t.descricao AS tipo_animal, COUNT(*) AS casos
        FROM ocorrencia o
        JOIN grau_acidente g ON o.id_grau        = g.id_grau
        JOIN evolucao      e ON o.id_evolucao    = e.id_evolucao
        JOIN tipo_animal   t ON o.id_tipo_animal = t.id_tipo_animal
        GROUP BY o.soroterapia, g.descricao, e.descricao, t.descricao
    """, conn)
    conn.close()
    df["soroterapia"] = df["soroterapia"].replace({"Nao": "Não"})
    df["evolucao"]    = df["evolucao"].replace(_EVOL_MAP)
    return df


_TEMPO_MAP = {
    "0 a 1 hora":    "Até 1 hora",
    "1 a 3 horas":   "De 1 a 3 horas",
    "3 a 6 horas":   "De 3 a 6 horas",
    "6 a 12 horas":  "De 6 a 12 horas",
    "12 a 24 horas": "De 12 a 24 horas",
    "24 e + horas":  "Mais de 24 horas",
}
_EVOL_MAP = {
    "Óbito pelo agravo notificado": "Óbito",
    "Óbito em investigação":        "Ign/Branco",
}


@st.cache_data
def load_tempo_grav():
    conn = _sqlite3.connect(_db_path())
    df = pd.read_sql_query("""
        SELECT g.descricao AS grau, ta.descricao AS tempo, e.descricao AS evolucao,
               t.descricao AS tipo_animal, COUNT(*) AS casos
        FROM ocorrencia o
        JOIN grau_acidente    g  ON o.id_grau              = g.id_grau
        JOIN tempo_atendimento ta ON o.id_tempo_atendimento = ta.id_tempo_atendimento
        JOIN evolucao          e  ON o.id_evolucao          = e.id_evolucao
        JOIN tipo_animal       t  ON o.id_tipo_animal       = t.id_tipo_animal
        GROUP BY g.descricao, ta.descricao, e.descricao, t.descricao
    """, conn)
    conn.close()
    df["tempo"]   = df["tempo"].replace(_TEMPO_MAP)
    df["evolucao"] = df["evolucao"].replace(_EVOL_MAP)
    return df


@st.cache_data
def load_discrepancia():
    conn = _sqlite3.connect(_db_path())
    df = pd.read_sql_query("""
        SELECT mr.nome_municipio AS municipio_residencia,
               mo.nome_municipio AS municipio_ocorrencia,
               t.descricao       AS tipo_animal,
               COUNT(*)          AS casos
        FROM ocorrencia o
        JOIN municipio   mr ON o.id_municipio_residencia = mr.id_municipio
        JOIN municipio   mo ON o.id_municipio_ocorrencia  = mo.id_municipio
        JOIN tipo_animal t  ON o.id_tipo_animal           = t.id_tipo_animal
        GROUP BY mr.nome_municipio, mo.nome_municipio, t.descricao
    """, conn)
    conn.close()
    return df


@st.cache_data
def load_local_picada():
    conn = _sqlite3.connect(_db_path())
    df = pd.read_sql_query("""
        SELECT lp.descricao AS local_picada, g.descricao AS grau,
               t.descricao  AS tipo_animal, o.faixa_etaria, o.sexo,
               COUNT(*)     AS casos
        FROM ocorrencia o
        JOIN local_picada  lp ON o.id_local_picada = lp.id_local_picada
        JOIN grau_acidente g  ON o.id_grau         = g.id_grau
        JOIN tipo_animal   t  ON o.id_tipo_animal   = t.id_tipo_animal
        GROUP BY lp.descricao, g.descricao, t.descricao, o.faixa_etaria, o.sexo
    """, conn)
    conn.close()
    return df


@st.cache_data
def load_acesso_saude():
    conn = _sqlite3.connect(_db_path())
    df = pd.read_sql_query("""
        SELECT ta.descricao AS tempo, e.descricao AS evolucao,
               m.nome_municipio AS municipio, g.descricao AS grau,
               COUNT(*) AS casos
        FROM ocorrencia o
        JOIN tempo_atendimento ta ON o.id_tempo_atendimento    = ta.id_tempo_atendimento
        JOIN evolucao           e  ON o.id_evolucao             = e.id_evolucao
        JOIN municipio          m  ON o.id_municipio_ocorrencia = m.id_municipio
        JOIN grau_acidente      g  ON o.id_grau                 = g.id_grau
        GROUP BY ta.descricao, e.descricao, m.nome_municipio, g.descricao
    """, conn)
    conn.close()
    df["tempo"]   = df["tempo"].replace(_TEMPO_MAP)
    df["evolucao"] = df["evolucao"].replace(_EVOL_MAP)
    return df
