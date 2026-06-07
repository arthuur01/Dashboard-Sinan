import streamlit as st
import plotly.graph_objects as go

ORDEM_LP   = ["Cabeça", "Tronco", "Membro superior", "Membro inferior", "Outros/NI"]
CORES_GRAU = {"Leve": "#4ade80", "Moderado": "#fbbf24", "Grave": "#f87171", "Ign/Branco": "#94a3b8"}


def render(df_lp):
    total_lp = int(df_lp["casos"].sum())
    regiao_mais_freq = (
        df_lp.groupby("local_picada")["casos"].sum().idxmax()
        if not df_lp.empty else "-"
    )
    pct_membros = round(
        df_lp[df_lp["local_picada"].isin(["Membro superior", "Membro inferior"])]["casos"].sum()
        / total_lp * 100, 1
    ) if total_lp > 0 else 0
    pct_grave_membros_inf = 0.0
    sub_mi = df_lp[df_lp["local_picada"] == "Membro inferior"]
    if not sub_mi.empty:
        tot_mi = sub_mi["casos"].sum()
        grav_mi = sub_mi[sub_mi["grau"] == "Grave"]["casos"].sum()
        pct_grave_membros_inf = round(grav_mi / tot_mi * 100, 1) if tot_mi > 0 else 0.0

    st.markdown("## Distribuição anatômica das picadas e gravidade")
    st.markdown("")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value" style="color:#4ade80;font-size:1.1rem">{regiao_mais_freq}</div>
            <div class="metric-label">Região Mais Atingida</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value" style="color:#4ade80">{pct_membros}%</div>
            <div class="metric-label">Picadas em Membros</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value" style="color:#f87171">{pct_grave_membros_inf}%</div>
            <div class="metric-label">% Grave em Membro Inferior</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value" style="color:#4ade80">{total_lp:,}</div>
            <div class="metric-label">Total de Registros</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("### 🗺️ Distribuição por Região do Corpo")
        df_total_lp = df_lp.groupby("local_picada")["casos"].sum().reset_index()
        df_total_lp = df_total_lp.sort_values("casos", ascending=False)
        fig_lp = go.Figure(go.Pie(
            labels=df_total_lp["local_picada"],
            values=df_total_lp["casos"],
            hole=0.4,
            marker=dict(colors=["#f97316","#a78bfa","#38bdf8","#4ade80","#94a3b8"],
                        line=dict(color="#0f1117", width=2)),
            texttemplate="%{label}<br>%{value:,} (%{percent})",
            textfont=dict(color="#f1f5f9", size=15),
        ))
        fig_lp.update_layout(
            showlegend=False,
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=10, r=10, t=10, b=10), height=360,
        )
        st.plotly_chart(fig_lp, width="stretch", key="t9_lp")

    with col_b:
        st.markdown("### ⚠️ Gravidade por Região do Corpo")
        df_grau_lp = df_lp.groupby(["local_picada", "grau"])["casos"].sum().reset_index()
        df_grau_lp = df_grau_lp[df_grau_lp["grau"].isin(["Leve", "Moderado", "Grave"])]
        fig_grau_lp = go.Figure()
        for grau in ["Leve", "Moderado", "Grave"]:
            sub = df_grau_lp[df_grau_lp["grau"] == grau].set_index("local_picada")
            regioes_ord = [r for r in ORDEM_LP if r in sub.index]
            vals = [int(sub.loc[r, "casos"]) if r in sub.index else 0 for r in regioes_ord]
            fig_grau_lp.add_trace(go.Bar(
                x=regioes_ord, y=vals, name=grau,
                marker=dict(color=CORES_GRAU[grau], line=dict(width=0)),
            ))
        fig_grau_lp.update_layout(
            barmode="stack", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(tickfont=dict(color="#cbd5e1", size=14)),
            yaxis=dict(tickfont=dict(color="#64748b"), gridcolor="#1e293b"),
            legend=dict(font=dict(color="#cbd5e1"), bgcolor="rgba(0,0,0,0)"),
            margin=dict(l=10, r=10, t=10, b=10), height=360,
        )
        st.plotly_chart(fig_grau_lp, width="stretch", key="t9_grau_lp")

    st.markdown("---")
    st.markdown("### 🐍 Localização da Picada por Tipo de Animal")
    df_anim_lp = df_lp.groupby(["local_picada", "tipo_animal"])["casos"].sum().reset_index()
    animais = [a for a in df_anim_lp["tipo_animal"].unique() if a != "Ign/Branco"]
    CORES_A = {"Serpente":"#f97316","Aranha":"#a78bfa","Escorpião":"#38bdf8",
               "Lagarta":"#4ade80","Abelha":"#fbbf24","Outros":"#94a3b8"}
    fig_anim_lp = go.Figure()
    for animal in animais:
        sub = df_anim_lp[df_anim_lp["tipo_animal"] == animal].set_index("local_picada")
        vals = [int(sub.loc[r, "casos"]) if r in sub.index else 0 for r in ORDEM_LP]
        fig_anim_lp.add_trace(go.Bar(
            x=ORDEM_LP, y=vals, name=animal,
            marker=dict(color=CORES_A.get(animal, "#94a3b8"), line=dict(width=0)),
        ))
    fig_anim_lp.update_layout(
        barmode="group", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(tickfont=dict(color="#cbd5e1")),
        yaxis=dict(tickfont=dict(color="#64748b"), gridcolor="#1e293b"),
        legend=dict(font=dict(color="#cbd5e1"), bgcolor="rgba(0,0,0,0)"),
        margin=dict(l=10, r=10, t=10, b=10), height=340,
    )
    st.plotly_chart(fig_anim_lp, width="stretch", key="t9_anim_lp")
