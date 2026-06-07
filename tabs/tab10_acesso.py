import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

ORDEM_TEMPO10 = ["Até 1 hora", "De 1 a 3 horas", "De 3 a 6 horas",
                 "De 6 a 12 horas", "De 12 a 24 horas", "Mais de 24 horas", "Ign/Branco"]
CORES_TEMPO10 = ["#4ade80", "#86efac", "#fbbf24", "#fb923c", "#f87171", "#dc2626", "#94a3b8"]
CORES_EVOL10  = {"Cura": "#4ade80", "Óbito": "#f87171",
                 "Óbito por outra causa": "#fb923c", "Ign/Branco": "#94a3b8"}


def render(df_as):
    tempo_order = [t for t in ORDEM_TEMPO10 if t in df_as["tempo"].unique()]

    total_casos_as   = int(df_as["casos"].sum())
    total_obitos_as  = int(df_as[df_as["evolucao"] == "Óbito"]["casos"].sum())
    taxa_mort_as     = round(total_obitos_as / total_casos_as * 100, 2) if total_casos_as > 0 else 0.0
    pct_rapido_as    = round(
        df_as[df_as["tempo"].isin(["Até 1 hora", "De 1 a 3 horas"])]["casos"].sum()
        / total_casos_as * 100, 1
    ) if total_casos_as > 0 else 0.0

    mun_mais_casos = (
        df_as.groupby("municipio")["casos"].sum().idxmax()
        if not df_as.empty else "-"
    )

    st.markdown("## Barreiras de acesso ao atendimento e seus impactos")
    st.markdown("")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value" style="color:#f87171">{taxa_mort_as}%</div>
            <div class="metric-label">Taxa de Mortalidade Geral</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value" style="color:#4ade80">{pct_rapido_as}%</div>
            <div class="metric-label">Atendidos em até 3 horas</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value" style="font-size:1rem;color:#38bdf8">{mun_mais_casos}</div>
            <div class="metric-label">Município com Mais Casos</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value" style="color:#38bdf8">{total_casos_as:,}</div>
            <div class="metric-label">Total de Registros</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("### ⏱️ Distribuição por Tempo de Atendimento")
    df_tempo_total = df_as.groupby("tempo")["casos"].sum()
    vals_tempo = [int(df_tempo_total.get(t, 0)) for t in tempo_order]
    cores_ord  = [CORES_TEMPO10[ORDEM_TEMPO10.index(t)] if t in ORDEM_TEMPO10 else "#94a3b8"
                  for t in tempo_order]
    fig_tempo = go.Figure(go.Bar(
        x=tempo_order, y=vals_tempo,
        marker=dict(color=cores_ord, line=dict(width=0)),
        text=[f"{v:,}" for v in vals_tempo],
        textposition="outside", textfont=dict(color="#f1f5f9", size=18),
    ))
    fig_tempo.update_layout(
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(tickfont=dict(color="#cbd5e1"), categoryorder="array", categoryarray=tempo_order, title_text="Intervalo de Atendimento", title_font=dict(color="#94a3b8")),
        yaxis=dict(tickfont=dict(color="#64748b"), gridcolor="#1e293b", title_text="Nº de Casos", title_font=dict(color="#94a3b8")),
        margin=dict(l=10, r=10, t=10, b=10), height=320,
    )
    st.plotly_chart(fig_tempo, width="stretch", key="t10_tempo")

    st.markdown("---")
    col_c, col_d = st.columns(2)
    with col_c:
        st.markdown("### ☠️ Taxa de Óbito por Tempo de Atendimento")
        df_obito_t = df_as.groupby(["tempo", "evolucao"])["casos"].sum().unstack(fill_value=0)
        if "Óbito" in df_obito_t.columns:
            df_obito_t["total"] = df_obito_t.sum(axis=1)
            df_obito_t["taxa"]  = (df_obito_t["Óbito"] / df_obito_t["total"] * 100).round(2).fillna(0)
            df_obito_t = df_obito_t.reindex(tempo_order).fillna(0)
            cores_ord2 = [CORES_TEMPO10[ORDEM_TEMPO10.index(t)] if t in ORDEM_TEMPO10 else "#94a3b8"
                          for t in tempo_order]
            fig_taxa = go.Figure(go.Bar(
                x=tempo_order, y=df_obito_t["taxa"].values,
                marker=dict(color=cores_ord2, line=dict(width=0)),
                text=[f"{v}%" for v in df_obito_t["taxa"].values],
                textposition="outside", textfont=dict(color="#f1f5f9", size=18),
            ))
            fig_taxa.update_layout(
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(tickfont=dict(color="#cbd5e1"), categoryorder="array", categoryarray=tempo_order, title_text="Intervalo de Atendimento", title_font=dict(color="#94a3b8")),
                yaxis=dict(tickfont=dict(color="#64748b"), gridcolor="#1e293b", ticksuffix="%", title_text="Taxa de Óbito (%)", title_font=dict(color="#94a3b8")),
                margin=dict(l=10, r=10, t=10, b=10), height=320,
            )
            st.plotly_chart(fig_taxa, width="stretch", key="t10_taxa")

    with col_d:
        st.markdown("### 🗺️ Top 15 Municípios com Maior Demora ≥ 12h")
        df_tarde = df_as[df_as["tempo"].isin(["De 12 a 24 horas", "Mais de 24 horas"])]
        top15 = (
            df_tarde.groupby("municipio")["casos"].sum()
            .nlargest(15).reset_index()
            .sort_values("casos")
        )
        fig_mun = go.Figure(go.Bar(
            x=top15["casos"], y=top15["municipio"], orientation="h",
            marker=dict(color="#f87171", line=dict(width=0)),
            text=top15["casos"].apply(lambda x: f"{x:,}"),
            textposition="outside", textfont=dict(color="#f1f5f9", size=17),
        ))
        fig_mun.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(tickfont=dict(color="#64748b"), gridcolor="#1e293b", title_text="Nº de Casos", title_font=dict(color="#94a3b8")),
            yaxis=dict(tickfont=dict(color="#cbd5e1", size=16), title_text="Município", title_font=dict(color="#94a3b8")),
            margin=dict(l=10, r=60, t=10, b=10), height=380,
        )
        st.plotly_chart(fig_mun, width="stretch", key="t10_mun")

    st.markdown("---")
    st.markdown("### 📊 Evolução de Desfecho por Grau de Acidente e Tempo")
    df_grau_t = (
        df_as[df_as["grau"].isin(["Leve", "Moderado", "Grave"])]
        .groupby(["tempo", "grau"])["casos"].sum()
        .unstack(fill_value=0)
        .reindex(tempo_order)
        .fillna(0)
    )
    fig_gt = go.Figure()
    CORES_GRAU_T = {"Leve": "#4ade80", "Moderado": "#fbbf24", "Grave": "#f87171"}
    for grau in ["Leve", "Moderado", "Grave"]:
        if grau in df_grau_t.columns:
            fig_gt.add_trace(go.Bar(
                x=tempo_order, y=df_grau_t[grau].values, name=grau,
                marker=dict(color=CORES_GRAU_T[grau], line=dict(width=0)),
            ))
    fig_gt.update_layout(
        barmode="group", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(tickfont=dict(color="#cbd5e1"), categoryorder="array", categoryarray=tempo_order, title_text="Intervalo de Atendimento", title_font=dict(color="#94a3b8")),
        yaxis=dict(tickfont=dict(color="#64748b"), gridcolor="#1e293b", title_text="Nº de Casos", title_font=dict(color="#94a3b8")),
        legend=dict(font=dict(color="#cbd5e1"), bgcolor="rgba(0,0,0,0)"),
        margin=dict(l=10, r=10, t=10, b=10), height=320,
    )
    st.plotly_chart(fig_gt, width="stretch", key="t10_gt")
