import streamlit as st
import plotly.graph_objects as go

CORES_A2 = {
    "Serpente": "#f97316", "Aranha": "#a78bfa",
    "Escorpião": "#38bdf8", "Lagarta": "#4ade80",
    "Abelha": "#fbbf24", "Outros": "#94a3b8",
}


def render(df_reg, df_trab_a2, df_serp_trab, df_aran_trab):
    total_rural_a2  = int(df_reg["rural"].sum())
    total_urbano_a2 = int(df_reg["urbano"].sum())
    pct_rural_a2    = round(total_rural_a2 / (total_rural_a2 + total_urbano_a2) * 100, 1)
    pct_trab_a2     = round(df_trab_a2["sim"].sum() / df_trab_a2["total"].sum() * 100, 1)
    animal_mais_rural = df_reg.sort_values("pct_rural", ascending=False).iloc[0]["tipo"]

    st.markdown("## Contexto situacional por tipo de animal")
    st.markdown("")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value" style="color:#38bdf8">{pct_rural_a2}%</div>
            <div class="metric-label">Casos em Zona Rural</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value" style="color:#38bdf8">{100 - pct_rural_a2}%</div>
            <div class="metric-label">Casos em Zona Urbana</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value" style="font-size:1.3rem;color:#38bdf8">{animal_mais_rural}</div>
            <div class="metric-label">Animal Mais Rural</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value" style="color:#38bdf8">{pct_trab_a2}%</div>
            <div class="metric-label">% Geral Vinculado ao Trabalho</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("### 🌿 Distribuição por Zona — Rural × Urbana")
    st.caption("Barras à esquerda = Zona Rural · Barras à direita = Zona Urbana")
    df_div = df_reg.sort_values("pct_rural", ascending=False).copy()
    fig_div = go.Figure()
    fig_div.add_trace(go.Bar(
        name="Zona Rural", y=df_div["tipo"], x=[-v for v in df_div["rural"]], orientation="h",
        marker=dict(color=[CORES_A2.get(t, "#64748b") for t in df_div["tipo"]], opacity=0.5, line=dict(width=0)),
        text=[f"{v:,}" for v in df_div["rural"]], textposition="inside",
        textfont=dict(color="#f1f5f9", size=11),
        hovertemplate="<b>%{y}</b><br>Zona Rural: %{customdata[0]:,} casos (%{customdata[1]}%)<extra></extra>",
        customdata=list(zip(df_div["rural"], df_div["pct_rural"])),
    ))
    fig_div.add_trace(go.Bar(
        name="Zona Urbana", y=df_div["tipo"], x=df_div["urbano"], orientation="h",
        marker=dict(color=[CORES_A2.get(t, "#64748b") for t in df_div["tipo"]], opacity=1.0, line=dict(width=0)),
        text=[f"{v:,}" for v in df_div["urbano"]], textposition="inside",
        textfont=dict(color="#0d1117", size=11),
        hovertemplate="<b>%{y}</b><br>Zona Urbana: %{x:,} casos (%{customdata}%)<extra></extra>",
        customdata=(100 - df_div["pct_rural"]).round(1),
    ))
    fig_div.add_vline(x=0, line_color="#475569", line_width=2)
    fig_div.update_layout(
        barmode="overlay", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(tickfont=dict(color="#64748b"), gridcolor="#1e293b",
                   zerolinecolor="#475569", zerolinewidth=2, tickformat=",d"),
        yaxis=dict(tickfont=dict(color="#e2e8f0", size=13)),
        legend=dict(font=dict(color="#cbd5e1"), bgcolor="rgba(0,0,0,0)", orientation="h", y=-0.15),
        margin=dict(l=10, r=20, t=10, b=40), height=360,
    )
    st.plotly_chart(fig_div, width="stretch", key="t2_div")

    st.markdown("---")
    st.markdown("### 💼 Proporção de Acidentes Relacionados ao Trabalho por Tipo")
    st.caption("Passe o mouse sobre cada barra para ver o detalhamento por espécie")

    def hover_com_especies(row):
        linhas = [f"<b>{row['tipo']}</b>",
                  f"Relacionado ao trabalho: {row['pct_trabalho']}%",
                  f"Casos: {row['sim']:,} de {row['total']:,}"]
        if row["tipo"] == "Serpente":
            linhas.append("<br><i>Espécies (% trabalho):</i>")
            for _, s in df_serp_trab.sort_values("pct_trabalho", ascending=False).iterrows():
                linhas.append(f"  · {s['especie']}: {s['pct_trabalho']}%")
        elif row["tipo"] == "Aranha":
            linhas.append("<br><i>Espécies (% trabalho):</i>")
            for _, s in df_aran_trab.sort_values("pct_trabalho", ascending=False).iterrows():
                linhas.append(f"  · {s['especie']}: {s['pct_trabalho']}%")
        return "<br>".join(linhas)

    df_trab_sorted = df_trab_a2.sort_values("pct_trabalho", ascending=False).copy()
    hover_texts = [hover_com_especies(row) for _, row in df_trab_sorted.iterrows()]
    fig_trab = go.Figure()
    fig_trab.add_trace(go.Bar(
        x=df_trab_sorted["tipo"], y=df_trab_sorted["pct_trabalho"],
        marker=dict(color=[CORES_A2.get(t, "#64748b") for t in df_trab_sorted["tipo"]], line=dict(width=0)),
        text=[f"{v}%" for v in df_trab_sorted["pct_trabalho"]],
        textposition="outside", textfont=dict(color="#f1f5f9", size=12),
        hovertemplate="%{customdata}<extra></extra>", customdata=hover_texts,
    ))
    fig_trab.update_layout(
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(tickfont=dict(color="#e2e8f0", size=13)),
        yaxis=dict(tickfont=dict(color="#64748b"), gridcolor="#1e293b",
                   ticksuffix="%", range=[0, df_trab_sorted["pct_trabalho"].max() * 1.25]),
        margin=dict(l=10, r=10, t=10, b=10), height=320,
    )
    st.plotly_chart(fig_trab, width="stretch", key="t2_trab")
