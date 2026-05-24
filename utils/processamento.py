import pandas as pd
import unicodedata
import re


def normalizar_nome(nome: str) -> str:
    """Remove acento, coloca uppercase, tira espaços extras."""
    if not isinstance(nome, str):
        return ""
    nome = unicodedata.normalize("NFKD", nome)
    nome = nome.encode("ascii", errors="ignore").decode("ascii")
    return nome.upper().strip()


def carregar_sinan(caminho: str) -> pd.DataFrame:
    """
    Lê o CSV do SINAN (formato TABNET) com cabeçalho sujo nas primeiras linhas.
    Retorna DataFrame limpo no formato longo: municipio | codigo_ibge | ano | total_acidentes
    """
    # Ler ignorando as 4 primeiras linhas de cabeçalho do TABNET
    df = pd.read_csv(
        caminho,
        sep=";",
        encoding="latin1",
        skiprows=4,
        header=0
    )

    # Remover linhas de rodapé (Total, Fonte, Notas, linhas vazias)
    col_municipio = df.columns[0]
    df = df[df[col_municipio].notna()]
    df = df[~df[col_municipio].str.strip().str.startswith(("Total", "Fonte", "Notas", " Fonte", " Notas"))]
    df = df[df[col_municipio].str.strip() != ""]

    # Separar código IBGE e nome do município (ex: "310010 Abadia dos Dourados")
    df["codigo_ibge"] = df[col_municipio].str.extract(r"^(\d+)")
    df["municipio_original"] = df[col_municipio].str.replace(r"^\d+\s*", "", regex=True).str.strip()
    df["municipio"] = df["municipio_original"].apply(normalizar_nome)

    # Colunas de anos (todas exceto municipio, Total, codigo_ibge, municipio_original)
    colunas_ano = [c for c in df.columns if re.match(r"^\d{4}$", str(c).strip())]

    # Converter para formato longo
    df_long = df[["municipio", "municipio_original", "codigo_ibge"] + colunas_ano].copy()
    df_long = df_long.melt(
        id_vars=["municipio", "municipio_original", "codigo_ibge"],
        value_vars=colunas_ano,
        var_name="ano",
        value_name="total_acidentes"
    )

    # Tratar valores "-" e NaN como 0
    df_long["total_acidentes"] = (
        df_long["total_acidentes"]
        .fillna("0")
        .astype(str)
        .str.strip()
        .replace({"-": "0", "": "0"})
        .astype(float)
        .astype(int)
    )
    df_long["ano"] = df_long["ano"].astype(int)

    # Remover município ignorado
    df_long = df_long[~df_long["municipio"].str.contains("IGNORADO", na=False)]

    return df_long.reset_index(drop=True)


def agregar_por_municipio(df: pd.DataFrame, anos: list) -> pd.DataFrame:
    """Agrega total de acidentes por município para os anos selecionados."""
    filtrado = df[df["ano"].isin(anos)]
    agg = (
        filtrado.groupby(["municipio", "municipio_original", "codigo_ibge"])["total_acidentes"]
        .sum()
        .reset_index()
        .sort_values("total_acidentes", ascending=False)
        .reset_index(drop=True)
    )
    agg["ranking"] = agg.index + 1
    return agg


def top10(df_agregado: pd.DataFrame) -> pd.DataFrame:
    return df_agregado.head(10)


def evolucao_total(df: pd.DataFrame) -> pd.DataFrame:
    """Total de acidentes por ano em MG."""
    return (
        df.groupby("ano")["total_acidentes"]
        .sum()
        .reset_index()
        .sort_values("ano")
    )