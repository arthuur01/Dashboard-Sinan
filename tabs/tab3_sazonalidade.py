import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

CORES_ANIMAL = {
    "Serpente": "#f97316", "Aranha": "#a78bfa",
    "Escorpião": "#38bdf8", "Lagarta": "#4ade80",
    "Abelha": "#fbbf24",
}
ORDEM_MESES = ["Jan","Fev","Mar","Abr","Mai","Jun","Jul","Ago","Set","Out","Nov","Dez"]


def render(df_sazonal):
    animais = [a for a in df_sazonal["tipo_animal"].unique() if a in CORES_ANIMAL]
    total_ano = df_sazonal.groupby("ano")["casos"].sum()
    pico_mes  = df_sazonal.groupby("mes_nome")["casos"].sum().idxmax()
    maior_ano = total_ano.idxmax()
    maior_val = int(total_ano.max())

    st.markdown("## Padrões temporais de ocorrência")
    st.markdown("")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value" style="color:#4ade80">{pico_mes}</div>
            <div class="metric-label">Mês de Pico Histórico</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value" style="color:#4ade80">{maior_ano}</div>
            <div class="metric-label">Ano com Mais Registros</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value" style="color:#4ade80">{maior_val:,}</div>
            <div class="metric-label">Total no Ano de Pico</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("### 🔄 Sazonalidade Mensal por Tipo de Animal")
    mensal = df_sazonal.groupby(["mes_nome", "tipo_animal"])["casos"].sum().reset_index()
    fig_sazon = go.Figure()
    for animal in animais:
        sub = mensal[mensal["tipo_animal"] == animal].set_index("mes_nome").reindex(ORDEM_MESES).fillna(0).reset_index()
        fig_sazon.add_trace(go.Scatter(
            x=sub["mes_nome"], y=sub["casos"], name=animal, mode="lines+markers",
            line=dict(color=CORES_ANIMAL[animal], width=3),
            marker=dict(size=8, color=CORES_ANIMAL[animal], line=dict(color="#0f1117", width=1)),
        ))
    fig_sazon.update_layout(
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(tickfont=dict(color="#cbd5e1"), gridcolor="#1e293b"),
        yaxis=dict(tickfont=dict(color="#64748b"), gridcolor="#1e293b"),
        legend=dict(font=dict(color="#cbd5e1"), bgcolor="rgba(0,0,0,0)"),
        margin=dict(l=10, r=10, t=10, b=10), height=350,
    )
    st.plotly_chart(fig_sazon, width="stretch", key="t3_sazon")

    st.markdown("---")
    st.markdown("### 📅 Evolução Anual por Tipo de Animal")
    anual = df_sazonal.groupby(["ano", "tipo_animal"])["casos"].sum().reset_index()
    anos_uniq = sorted(anual["ano"].unique())
    fig_evo = go.Figure()
    for animal in animais:
        sub = anual[anual["tipo_animal"] == animal]
        fig_evo.add_trace(go.Bar(
            x=sub["ano"], y=sub["casos"], name=animal,
            marker=dict(color=CORES_ANIMAL[animal], line=dict(width=0)),
        ))
    fig_evo.update_layout(
        barmode="stack", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(tickvals=anos_uniq, ticktext=[str(a) for a in anos_uniq],
                   tickfont=dict(color="#cbd5e1"), gridcolor="#1e293b"),
        yaxis=dict(tickfont=dict(color="#64748b"), gridcolor="#1e293b"),
        legend=dict(font=dict(color="#cbd5e1"), bgcolor="rgba(0,0,0,0)"),
        margin=dict(l=10, r=10, t=10, b=10), height=320,
    )
    st.plotly_chart(fig_evo, width="stretch", key="t3_evo")

    st.markdown("---")
    st.markdown("### 🌡️ Mapa de Calor — Meses × Tipo de Animal")
    pivot = df_sazonal.groupby(["mes_nome", "tipo_animal"])["casos"].sum().unstack(fill_value=0)
    pivot = pivot.reindex([m for m in ORDEM_MESES if m in pivot.index])
    fig_hm = go.Figure(go.Heatmap(
        z=pivot.values, x=list(pivot.columns), y=list(pivot.index),
        colorscale="YlOrRd", showscale=True,
        text=pivot.values, texttemplate="%{text:,}",
        hovertemplate="Animal: %{x}<br>Mês: %{y}<br>Casos: %{z:,}<extra></extra>",
    ))
    fig_hm.update_layout(
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(tickfont=dict(color="#cbd5e1")),
        yaxis=dict(tickfont=dict(color="#cbd5e1")),
        margin=dict(l=10, r=10, t=10, b=10), height=360,
    )
    st.plotly_chart(fig_hm, width="stretch", key="t3_hm")
