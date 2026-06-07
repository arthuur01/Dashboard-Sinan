import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

FAIXAS_TEMPO = ["Até 1 hora", "De 1 a 3 horas", "De 3 a 6 horas", "De 6 a 12 horas",
                "De 12 a 24 horas", "Mais de 24 horas", "Ign/Branco"]
CORES_TEMPO  = ["#4ade80", "#86efac", "#fbbf24", "#fb923c", "#f87171", "#dc2626", "#94a3b8"]


def render(df_tg):
    # pré-processa
    tempo_order = [t for t in FAIXAS_TEMPO if t in df_tg["tempo"].unique()]
    df_grave    = df_tg[df_tg["grau"] == "Grave"]
    total_grave = int(df_grave["casos"].sum()) if not df_grave.empty else 0
    if not df_grave.empty and total_grave > 0:
        obitos_grave = int(df_grave[df_grave["evolucao"] == "Óbito"]["casos"].sum())
        pct_obito_grave = round(obitos_grave / total_grave * 100, 1)
    else:
        obitos_grave = 0
        pct_obito_grave = 0.0
    tempo_mais_obitos = (
        df_tg[df_tg["evolucao"] == "Óbito"]
        .groupby("tempo")["casos"].sum()
        .reindex(tempo_order).fillna(0)
        .idxmax()
    ) if not df_tg[df_tg["evolucao"] == "Óbito"].empty else "-"

    st.markdown("## Relação entre tempo de atendimento, gravidade e desfecho")
    st.markdown("")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value" style="color:#f87171">{pct_obito_grave}%</div>
            <div class="metric-label">Óbitos em Casos Graves</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value" style="color:#f87171;font-size:1.1rem">{tempo_mais_obitos}</div>
            <div class="metric-label">Intervalo com Mais Óbitos</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value" style="color:#f87171">{obitos_grave:,}</div>
            <div class="metric-label">Óbitos em Casos Graves</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("### ⏱️ Casos por Intervalo de Atendimento e Grau")
    df_tg_pivot = (
        df_tg.groupby(["tempo", "grau"])["casos"].sum()
        .unstack(fill_value=0)
        .reindex(tempo_order)
    )
    fig_bar = go.Figure()
    CORES_GRAU = {"Leve": "#4ade80", "Moderado": "#fbbf24", "Grave": "#f87171", "Ign/Branco": "#94a3b8"}
    for grau in ["Leve", "Moderado", "Grave"]:
        if grau in df_tg_pivot.columns:
            fig_bar.add_trace(go.Bar(
                x=tempo_order, y=df_tg_pivot[grau].values, name=grau,
                marker=dict(color=CORES_GRAU[grau], line=dict(width=0)),
            ))
    fig_bar.update_layout(
        barmode="group", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(tickfont=dict(color="#cbd5e1"), categoryorder="array", categoryarray=tempo_order, title_text="Intervalo de Atendimento", title_font=dict(color="#94a3b8")),
        yaxis=dict(tickfont=dict(color="#64748b"), gridcolor="#1e293b", title_text="Nº de Casos", title_font=dict(color="#94a3b8")),
        legend=dict(font=dict(color="#cbd5e1"), bgcolor="rgba(0,0,0,0)"),
        margin=dict(l=10, r=10, t=10, b=10), height=340,
    )
    st.plotly_chart(fig_bar, width="stretch", key="t6_bar")

    st.markdown("---")
    st.markdown("### ☠️ Taxa de Óbito por Intervalo de Atendimento")
    df_obito_tempo = (
        df_tg.groupby(["tempo", "evolucao"])["casos"].sum()
        .unstack(fill_value=0)
        .reindex(tempo_order)
    )
    if "Óbito" in df_obito_tempo.columns:
        df_obito_tempo["total"] = df_obito_tempo.sum(axis=1)
        df_obito_tempo["taxa"]  = (df_obito_tempo["Óbito"] / df_obito_tempo["total"] * 100).round(2).fillna(0)
        cores_barras = [CORES_TEMPO[i] if i < len(CORES_TEMPO) else "#64748b" for i in range(len(tempo_order))]
        fig_taxa = go.Figure(go.Bar(
            x=tempo_order, y=df_obito_tempo["taxa"].values,
            marker=dict(color=cores_barras, line=dict(width=0)),
            text=[f"{v}%" for v in df_obito_tempo["taxa"].values],
            textposition="outside", textfont=dict(color="#f1f5f9", size=18),
        ))
        fig_taxa.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(tickfont=dict(color="#cbd5e1"), categoryorder="array", categoryarray=tempo_order, title_text="Intervalo de Atendimento", title_font=dict(color="#94a3b8")),
            yaxis=dict(tickfont=dict(color="#64748b"), gridcolor="#1e293b", ticksuffix="%", title_text="Taxa de Óbito (%)", title_font=dict(color="#94a3b8")),
            margin=dict(l=10, r=10, t=10, b=10), height=320,
        )
        st.plotly_chart(fig_taxa, width="stretch", key="t6_taxa")

    st.markdown("---")
    st.markdown("### 🌡️ Mapa de Calor — Intervalo de Atendimento × Tipo de Animal")
    df_hm = (
        df_tg.groupby(["tempo", "tipo_animal"])["casos"].sum()
        .unstack(fill_value=0)
        .reindex(tempo_order)
    )
    fig_hm = go.Figure(go.Heatmap(
        z=df_hm.values, x=list(df_hm.columns), y=list(df_hm.index),
        colorscale="YlOrRd", showscale=True,
        text=df_hm.values, texttemplate="%{text:,}",
        hovertemplate="Animal: %{x}<br>Intervalo: %{y}<br>Casos: %{z:,}<extra></extra>",
    ))
    fig_hm.update_layout(
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(tickfont=dict(color="#cbd5e1"), title_text="Tipo de Animal", title_font=dict(color="#94a3b8")),
        yaxis=dict(tickfont=dict(color="#cbd5e1"), title_text="Intervalo de Atendimento", title_font=dict(color="#94a3b8")),
        margin=dict(l=10, r=10, t=10, b=10), height=380,
    )
    st.plotly_chart(fig_hm, width="stretch", key="t6_hm")
