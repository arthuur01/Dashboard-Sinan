import streamlit as st
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.data_loader import (
    load_data, get_gdf_merged, load_animal_data,
    load_sazonalidade, load_demografico, load_desfecho,
    load_tempo_grav, load_discrepancia, load_local_picada, load_acesso_saude,
)
from utils.processamento import top10, evolucao_total
from tabs.tab1_geografico  import render as render_tab1
from tabs.tab2_animal      import render as render_tab2
from tabs.tab3_sazonalidade import render as render_tab3
from tabs.tab4_demografico  import render as render_tab4
from tabs.tab5_desfecho     import render as render_tab5
from tabs.tab6_triangulo    import render as render_tab6
from tabs.tab7_discrepancia import render as render_tab7
from tabs.tab8_soroterapia  import render as render_tab8
from tabs.tab9_picada       import render as render_tab9
from tabs.tab10_acesso      import render as render_tab10

# ── Configuração ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Acidentes Ofídicos — MG",
    page_icon="🐍",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    [data-testid="stAppViewContainer"] { background-color: #0f1117; }
    [data-testid="stSidebar"]          { background-color: #161b22; }
    .metric-card {
        background: linear-gradient(135deg, #1e2736, #1a2332);
        border: 1px solid #2d3748;
        border-radius: 12px;
        padding: 16px 20px;
        text-align: center;
    }
    .metric-value { font-size: 2rem; font-weight: 700; color: #f97316; }
    .metric-label { font-size: 0.8rem; color: #94a3b8; margin-top: 4px; }
    h1, h2, h3 { color: #f1f5f9 !important; }
    .stMarkdown p { color: #cbd5e1; }
</style>
""", unsafe_allow_html=True)

# ── Carregar dados ────────────────────────────────────────────────────────────
df_raw, gdf          = load_data()
anos_disponiveis     = sorted(df_raw["ano"].unique().tolist())
df_reg, df_trab_a2, df_serp_trab, df_aran_trab = load_animal_data()
df_sazonal           = load_sazonalidade()
df_demog             = load_demografico()
df_desfecho          = load_desfecho()
df_tg                = load_tempo_grav()
df_disc              = load_discrepancia()
df_lp                = load_local_picada()
df_as                = load_acesso_saude()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🐍 Filtros")
    st.markdown("---")
    anos_sel = st.multiselect(
        "📅 Ano(s) do acidente",
        options=anos_disponiveis,
        default=anos_disponiveis,
        help="Selecione um ou mais anos para filtrar os dados",
    )
    if not anos_sel:
        anos_sel = anos_disponiveis
    st.markdown("---")
    tipo_mapa = st.radio(
        "🗺️ Tipo de visualização",
        ["Choropleth (intensidade por município)", "Heatmap (densidade de pontos)"],
        index=0,
    )
    st.markdown("---")
    st.markdown("""
    <div style='font-size:0.75rem; color:#64748b; line-height:1.6'>
    📊 Fonte: SINAN/CPDE/SVE/SUBVS/SESMG<br>
    🔬 Casos confirmados de acidentes com animais peçonhentos<br>
    📍 Filtrado por: UF Acidente = Minas Gerais
    </div>
    """, unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("# 🐍 Acidentes com Animais Peçonhentos — Minas Gerais")
st.markdown("**Análises integradas dos dados do SINAN** | Fonte: SINAN/CPDE/SVE/SUBVS/SESMG")
st.markdown("---")

# ── Abas ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10 = st.tabs([
    "🗺️ Análise Geográfica",
    "🦂 Perfil do Animal",
    "📅 Sazonalidade",
    "👥 Vulnerabilidade Demográfica",
    "💉 Desfecho Clínico",
    "⏱️ Triângulo Crítico",
    "📍 Discrepância Geográfica",
    "💊 Eficácia da Soroterapia",
    "🦴 Localização da Picada",
    "🏥 Acesso à Saúde",
])

with tab1:
    render_tab1(df_raw, gdf, anos_sel, tipo_mapa, get_gdf_merged, top10, evolucao_total)
with tab2:
    render_tab2(df_reg, df_trab_a2, df_serp_trab, df_aran_trab)
with tab3:
    render_tab3(df_sazonal)
with tab4:
    render_tab4(df_demog)
with tab5:
    render_tab5(df_desfecho)
with tab6:
    render_tab6(df_tg)
with tab7:
    render_tab7(df_disc)
with tab8:
    render_tab8(df_desfecho)
with tab9:
    render_tab9(df_lp)
with tab10:
    render_tab10(df_as)
