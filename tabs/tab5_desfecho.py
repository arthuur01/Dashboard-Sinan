import streamlit as st
import plotly.graph_objects as go

CORES_EVOLUCAO = {
    "Cura":              "#4ade80",
    "Óbito":             "#f87171",
    "Óbito por outra causa": "#fb923c",
    "Ign/Branco":        "#94a3b8",
}
ORDEM_GRAU = ["Leve", "Moderado", "Grave", "Ign/Branco"]


def render(df_desfecho):
    total_obito     = int(df_desfecho[df_desfecho["evolucao"] == "Óbito"]["casos"].sum())
    total_casos_d   = int(df_desfecho["casos"].sum())
    taxa_mortal     = round(total_obito / total_casos_d * 100, 2) if total_casos_d > 0 else 0
    pct_soro        = round(df_desfecho[df_desfecho["soroterapia"] == "Sim"]["casos"].sum() / total_casos_d * 100, 1)
    grau_maior      = df_desfecho.groupby("grau")["casos"].sum().drop("Ign/Branco", errors="ignore").idxmax()

    st.markdown("## Padrões de evolução clínica e mortalidade")
    st.markdown("")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value" style="color:#f87171">{taxa_mortal}%</div>
            <div class="metric-label">Taxa de Mortalidade</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value" style="color:#4ade80">{pct_soro}%</div>
            <div class="metric-label">Casos com Soroterapia</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value" style="color:#fbbf24;font-size:1.3rem">{grau_maior}</div>
            <div class="metric-label">Grau de Acidente Mais Comum</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("### 💊 Desfecho por Soroterapia")
        df_soro = df_desfecho.groupby(["soroterapia", "evolucao"])["casos"].sum().reset_index()
        df_soro = df_soro[df_soro["soroterapia"].isin(["Sim", "Não"])]
        fig_soro = go.Figure()
        for evol, cor in CORES_EVOLUCAO.items():
            sub = df_soro[df_soro["evolucao"] == evol]
            if sub["casos"].sum() == 0:
                continue
            fig_soro.add_trace(go.Bar(
                x=sub["soroterapia"], y=sub["casos"], name=evol,
                marker=dict(color=cor, line=dict(width=0)),
            ))
        fig_soro.update_layout(
            barmode="stack", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(tickfont=dict(color="#e2e8f0"), title_text="Uso de Soroterapia", title_font=dict(color="#94a3b8")),
            yaxis=dict(tickfont=dict(color="#64748b"), gridcolor="#1e293b", title_text="Nº de Casos", title_font=dict(color="#94a3b8")),
            legend=dict(font=dict(color="#cbd5e1"), bgcolor="rgba(0,0,0,0)"),
            margin=dict(l=10, r=10, t=10, b=10), height=330,
        )
        st.plotly_chart(fig_soro, width="stretch", key="t5_soro")

    with col_b:
        st.markdown("### 📊 Desfecho por Grau de Acidente")
        df_grau_evol = df_desfecho.groupby(["grau", "evolucao"])["casos"].sum().reset_index()
        df_grau_evol = df_grau_evol[df_grau_evol["grau"].isin(ORDEM_GRAU)]
        fig_grau = go.Figure()
        for evol, cor in CORES_EVOLUCAO.items():
            sub = df_grau_evol[df_grau_evol["evolucao"] == evol]
            if sub["casos"].sum() == 0:
                continue
            sub_sorted = sub.set_index("grau").reindex(ORDEM_GRAU).fillna(0).reset_index()
            fig_grau.add_trace(go.Bar(
                x=sub_sorted["grau"], y=sub_sorted["casos"], name=evol,
                marker=dict(color=cor, line=dict(width=0)),
            ))
        fig_grau.update_layout(
            barmode="stack", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(tickfont=dict(color="#e2e8f0"),
                       categoryorder="array", categoryarray=ORDEM_GRAU,
                       title_text="Grau de Acidente", title_font=dict(color="#94a3b8")),
            yaxis=dict(tickfont=dict(color="#64748b"), gridcolor="#1e293b", title_text="Nº de Casos", title_font=dict(color="#94a3b8")),
            legend=dict(font=dict(color="#cbd5e1"), bgcolor="rgba(0,0,0,0)"),
            margin=dict(l=10, r=10, t=10, b=10), height=330,
        )
        st.plotly_chart(fig_grau, width="stretch", key="t5_grau")

    st.markdown("---")
    st.markdown("### 🐍 Taxa de Mortalidade por Tipo de Animal")
    df_mortal_animal = df_desfecho.groupby(["tipo_animal", "evolucao"])["casos"].sum().unstack(fill_value=0)
    if "Óbito" in df_mortal_animal.columns:
        df_mortal_animal["taxa_mort"] = (
            df_mortal_animal["Óbito"] / df_mortal_animal.sum(axis=1) * 100
        ).round(2)
        df_mortal_animal = df_mortal_animal.sort_values("taxa_mort", ascending=False).reset_index()
        fig_anim = go.Figure(go.Bar(
            x=df_mortal_animal["tipo_animal"], y=df_mortal_animal["taxa_mort"],
            marker=dict(color="#f87171", line=dict(width=0)),
            text=[f"{v}%" for v in df_mortal_animal["taxa_mort"]],
            textposition="outside", textfont=dict(color="#f1f5f9", size=18),
        ))
        fig_anim.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(tickfont=dict(color="#e2e8f0"), title_text="Tipo de Animal", title_font=dict(color="#94a3b8")),
            yaxis=dict(tickfont=dict(color="#64748b"), gridcolor="#1e293b", ticksuffix="%", title_text="Taxa de Mortalidade (%)", title_font=dict(color="#94a3b8")),
            margin=dict(l=10, r=10, t=10, b=10), height=300,
        )
        st.plotly_chart(fig_anim, width="stretch", key="t5_anim")
