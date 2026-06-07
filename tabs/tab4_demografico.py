import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

ORDEM_FAIXAS = ["<1 Ano", "1-4", "5-9", "10-14", "15-19", "20-39", "40-59", "60-64", "65-69", "70-79", "80 e +"]
CORES_RACA   = {
    "Branca": "#e2e8f0", "Preta": "#4b5563", "Amarela": "#fbbf24",
    "Parda": "#c2845f", "Indígena": "#22c55e", "Ign/Branco": "#475569",
}


def render(df_demog):
    total_masc  = int(df_demog[df_demog["sexo"] == "Masculino"]["casos"].sum())
    total_fem   = int(df_demog[df_demog["sexo"] == "Feminino"]["casos"].sum())
    pct_masc    = round(total_masc / (total_masc + total_fem) * 100, 1) if (total_masc + total_fem) > 0 else 0
    faixa_maior = df_demog.groupby("faixa_etaria")["casos"].sum().idxmax()

    st.markdown("## Vulnerabilidade por perfil sociodemográfico")
    st.markdown("")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value" style="color:#a78bfa">{pct_masc}%</div>
            <div class="metric-label">Casos em Homens</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value" style="color:#a78bfa">{100 - pct_masc}%</div>
            <div class="metric-label">Casos em Mulheres</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value" style="color:#a78bfa;font-size:1.3rem">{faixa_maior}</div>
            <div class="metric-label">Faixa Etária Mais Afetada</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("### 👤 Distribuição por Sexo")
        df_sexo = df_demog.groupby("sexo")["casos"].sum().reset_index()
        df_sexo = df_sexo[df_sexo["sexo"].isin(["Masculino", "Feminino"])]
        fig_sexo = go.Figure(go.Pie(
            labels=df_sexo["sexo"], values=df_sexo["casos"],
            hole=0.55,
            marker=dict(colors=["#38bdf8", "#f472b6"],
                        line=dict(color="#0f1117", width=2)),
            texttemplate="%{label}<br>%{value:,} (%{percent})",
            textfont=dict(color="#f1f5f9", size=20),
        ))
        fig_sexo.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            showlegend=False,
            margin=dict(l=10, r=10, t=20, b=10), height=300,
        )
        st.plotly_chart(fig_sexo, width="stretch", key="t4_sexo")

    with col_b:
        st.markdown("### 🎨 Distribuição por Raça/Cor")
        df_raca = df_demog.groupby("raca")["casos"].sum().reset_index()
        df_raca = df_raca[df_raca["raca"] != "Ign/Branco"].sort_values("casos", ascending=False)
        fig_raca = go.Figure(go.Bar(
            x=df_raca["raca"], y=df_raca["casos"],
            marker=dict(color=[CORES_RACA.get(r, "#64748b") for r in df_raca["raca"]], line=dict(width=0)),
            text=df_raca["casos"].apply(lambda x: f"{x:,}"),
            textposition="outside", textfont=dict(color="#f1f5f9", size=18),
        ))
        fig_raca.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(tickfont=dict(color="#e2e8f0"), title_text="Raça/Cor", title_font=dict(color="#94a3b8")),
            yaxis=dict(tickfont=dict(color="#64748b"), gridcolor="#1e293b", title_text="Nº de Casos", title_font=dict(color="#94a3b8")),
            margin=dict(l=10, r=10, t=10, b=10), height=300,
        )
        st.plotly_chart(fig_raca, width="stretch", key="t4_raca")

    st.markdown("---")
    st.markdown("### 📊 Pirâmide Etária — Masculino × Feminino")
    df_masc = df_demog[df_demog["sexo"] == "Masculino"].groupby("faixa_etaria")["casos"].sum()
    df_fem  = df_demog[df_demog["sexo"] == "Feminino"].groupby("faixa_etaria")["casos"].sum()
    faixas  = [f for f in ORDEM_FAIXAS if f in df_masc.index or f in df_fem.index]
    v_masc  = [-int(df_masc.get(f, 0)) for f in faixas]
    v_fem   = [int(df_fem.get(f, 0)) for f in faixas]
    fig_pir = go.Figure()
    fig_pir.add_trace(go.Bar(
        y=faixas, x=v_masc, orientation="h", name="Masculino",
        marker=dict(color="#38bdf8", line=dict(width=0)),
        text=[f"{abs(v):,}" for v in v_masc], textposition="inside",
        textfont=dict(color="#0d1117", size=17),
    ))
    fig_pir.add_trace(go.Bar(
        y=faixas, x=v_fem, orientation="h", name="Feminino",
        marker=dict(color="#f472b6", line=dict(width=0)),
        text=[f"{v:,}" for v in v_fem], textposition="inside",
        textfont=dict(color="#0d1117", size=17),
    ))
    fig_pir.update_layout(
        barmode="overlay",
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(tickfont=dict(color="#64748b"), gridcolor="#1e293b",
                   tickformat=",d", zerolinecolor="#475569", zerolinewidth=2,
                   title_text="Nº de Casos (← Masc | Fem →)", title_font=dict(color="#94a3b8")),
        yaxis=dict(tickfont=dict(color="#cbd5e1", size=18), title_text="Faixa Etária", title_font=dict(color="#94a3b8")),
        legend=dict(font=dict(color="#cbd5e1"), bgcolor="rgba(0,0,0,0)", orientation="h", y=-0.12),
        margin=dict(l=10, r=10, t=10, b=40), height=420,
    )
    st.plotly_chart(fig_pir, width="stretch", key="t4_pir")
