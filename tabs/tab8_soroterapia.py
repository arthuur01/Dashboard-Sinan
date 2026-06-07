import streamlit as st
import plotly.graph_objects as go

CORES_SORO  = {"Sim": "#4ade80", "Não": "#f87171", "Ign/Branco": "#94a3b8"}
ORDEM_SORO  = ["Sim", "Não", "Ign/Branco"]
ORDEM_GRAU8 = ["Leve", "Moderado", "Grave", "Ign/Branco"]


def render(df_desfecho):
    df_s = df_desfecho[df_desfecho["soroterapia"].isin(["Sim", "Não"])].copy()
    total_com    = int(df_s[df_s["soroterapia"] == "Sim"]["casos"].sum())
    total_sem    = int(df_s[df_s["soroterapia"] == "Não"]["casos"].sum())
    total_s      = total_com + total_sem

    # taxa de óbito com vs sem soroterapia
    def taxa_obito(sub):
        tot = sub["casos"].sum()
        obi = sub[sub["evolucao"] == "Óbito"]["casos"].sum()
        return round(obi / tot * 100, 2) if tot > 0 else 0.0

    taxa_com_soro = taxa_obito(df_s[df_s["soroterapia"] == "Sim"])
    taxa_sem_soro = taxa_obito(df_s[df_s["soroterapia"] == "Não"])
    reducao       = round(taxa_sem_soro - taxa_com_soro, 2)

    st.markdown("## Impacto da soroterapia na mortalidade")
    st.markdown("")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value" style="color:#4ade80">{taxa_com_soro}%</div>
            <div class="metric-label">Mortalidade COM Soroterapia</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value" style="color:#f87171">{taxa_sem_soro}%</div>
            <div class="metric-label">Mortalidade SEM Soroterapia</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value" style="color:#fbbf24">-{reducao}pp</div>
            <div class="metric-label">Redução de Mortalidade</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        pct_com = round(total_com / total_s * 100, 1) if total_s > 0 else 0
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value" style="color:#4ade80">{pct_com}%</div>
            <div class="metric-label">Cobertura de Soroterapia</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("### 📊 Taxa de Óbito por Uso de Soroterapia")
        fig_comp = go.Figure(go.Bar(
            x=["COM Soroterapia", "SEM Soroterapia"],
            y=[taxa_com_soro, taxa_sem_soro],
            marker=dict(color=["#4ade80", "#f87171"], line=dict(width=0)),
            text=[f"{taxa_com_soro}%", f"{taxa_sem_soro}%"],
            textposition="outside", textfont=dict(color="#f1f5f9", size=20),
        ))
        fig_comp.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(tickfont=dict(color="#e2e8f0", size=17)),
            yaxis=dict(tickfont=dict(color="#64748b"), gridcolor="#1e293b", ticksuffix="%"),
            margin=dict(l=10, r=10, t=10, b=10), height=320,
        )
        st.plotly_chart(fig_comp, width="stretch", key="t8_comp")

    with col_b:
        st.markdown("### 🐍 Taxa de Óbito por Tipo de Animal × Soroterapia")
        df_anim = (
            df_s[~df_s["tipo_animal"].isin(["Ign/Branco"])]
            .groupby(["tipo_animal", "soroterapia", "evolucao"])["casos"].sum()
            .reset_index()
        )
        animais = df_anim["tipo_animal"].unique()
        fig_anim = go.Figure()
        for soro in ["Sim", "Não"]:
            taxas = []
            for animal in animais:
                sub = df_anim[(df_anim["tipo_animal"] == animal) & (df_anim["soroterapia"] == soro)]
                taxas.append(taxa_obito(sub))
            fig_anim.add_trace(go.Bar(
                x=list(animais), y=taxas, name=f"Soroterapia: {soro}",
                marker=dict(color=CORES_SORO[soro], line=dict(width=0)),
                text=[f"{t}%" for t in taxas],
                textposition="outside", textfont=dict(color="#f1f5f9", size=14),
            ))
        fig_anim.update_layout(
            barmode="group", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(tickfont=dict(color="#e2e8f0")),
            yaxis=dict(tickfont=dict(color="#64748b"), gridcolor="#1e293b", ticksuffix="%"),
            legend=dict(font=dict(color="#cbd5e1"), bgcolor="rgba(0,0,0,0)"),
            margin=dict(l=10, r=10, t=10, b=10), height=320,
        )
        st.plotly_chart(fig_anim, width="stretch", key="t8_anim")

    st.markdown("---")
    st.markdown("### 📈 Eficácia por Grau de Acidente")
    df_grau_s = (
        df_s[df_s["grau"].isin(["Leve", "Moderado", "Grave"])]
        .groupby(["grau", "soroterapia", "evolucao"])["casos"].sum()
        .reset_index()
    )
    fig_grau = go.Figure()
    for soro in ["Sim", "Não"]:
        taxas_g = []
        for grau in ORDEM_GRAU8[:3]:
            sub = df_grau_s[(df_grau_s["grau"] == grau) & (df_grau_s["soroterapia"] == soro)]
            taxas_g.append(taxa_obito(sub))
        fig_grau.add_trace(go.Bar(
            x=ORDEM_GRAU8[:3], y=taxas_g, name=f"Soroterapia: {soro}",
            marker=dict(color=CORES_SORO[soro], line=dict(width=0)),
            text=[f"{t}%" for t in taxas_g],
            textposition="outside", textfont=dict(color="#f1f5f9", size=15),
        ))
    fig_grau.update_layout(
        barmode="group", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(tickfont=dict(color="#e2e8f0")),
        yaxis=dict(tickfont=dict(color="#64748b"), gridcolor="#1e293b", ticksuffix="%"),
        legend=dict(font=dict(color="#cbd5e1"), bgcolor="rgba(0,0,0,0)"),
        margin=dict(l=10, r=10, t=10, b=10), height=320,
    )
    st.plotly_chart(fig_grau, width="stretch", key="t8_grau")
