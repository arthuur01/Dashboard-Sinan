import streamlit as st
import plotly.graph_objects as go


def render(df_disc):
    df_cruzado = df_disc[
        df_disc["municipio_residencia"] != df_disc["municipio_ocorrencia"]
    ].copy()
    total_disc   = int(df_cruzado["casos"].sum())
    total_todos  = int(df_disc["casos"].sum())
    pct_disc     = round(total_disc / total_todos * 100, 1) if total_todos > 0 else 0
    top_origem   = df_cruzado.groupby("municipio_residencia")["casos"].sum().idxmax() if not df_cruzado.empty else "-"
    top_destino  = df_cruzado.groupby("municipio_ocorrencia")["casos"].sum().idxmax() if not df_cruzado.empty else "-"

    st.markdown("## Fluxo de deslocamento para tratamento")
    st.markdown("")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value" style="color:#38bdf8">{pct_disc}%</div>
            <div class="metric-label">Casos com Deslocamento</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value" style="color:#38bdf8">{total_disc:,}</div>
            <div class="metric-label">Total de Atendimentos Fora do Município</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value" style="font-size:1rem;color:#38bdf8">{top_origem}</div>
            <div class="metric-label">Principal Origem de Pacientes</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value" style="font-size:1rem;color:#38bdf8">{top_destino}</div>
            <div class="metric-label">Principal Destino de Atendimento</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("### 🏘️ Top 10 Municípios de Origem")
        top_orig = (
            df_cruzado.groupby("municipio_residencia")["casos"].sum()
            .nlargest(10).reset_index()
            .sort_values("casos")
        )
        fig_orig = go.Figure(go.Bar(
            x=top_orig["casos"], y=top_orig["municipio_residencia"], orientation="h",
            marker=dict(color="#38bdf8", line=dict(width=0)),
            text=top_orig["casos"].apply(lambda x: f"{x:,}"),
            textposition="outside", textfont=dict(color="#f1f5f9", size=18),
        ))
        fig_orig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(tickfont=dict(color="#64748b"), gridcolor="#1e293b", title_text="Nº de Casos", title_font=dict(color="#94a3b8")),
            yaxis=dict(tickfont=dict(color="#cbd5e1", size=17), title_text="Município de Residência", title_font=dict(color="#94a3b8")),
            margin=dict(l=10, r=60, t=10, b=10), height=380,
        )
        st.plotly_chart(fig_orig, width="stretch", key="t7_orig")

    with col_b:
        st.markdown("### 🏥 Top 10 Municípios de Destino")
        top_dest = (
            df_cruzado.groupby("municipio_ocorrencia")["casos"].sum()
            .nlargest(10).reset_index()
            .sort_values("casos")
        )
        fig_dest = go.Figure(go.Bar(
            x=top_dest["casos"], y=top_dest["municipio_ocorrencia"], orientation="h",
            marker=dict(color="#fb923c", line=dict(width=0)),
            text=top_dest["casos"].apply(lambda x: f"{x:,}"),
            textposition="outside", textfont=dict(color="#f1f5f9", size=18),
        ))
        fig_dest.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(tickfont=dict(color="#64748b"), gridcolor="#1e293b", title_text="Nº de Casos", title_font=dict(color="#94a3b8")),
            yaxis=dict(tickfont=dict(color="#cbd5e1", size=17), title_text="Município de Atendimento", title_font=dict(color="#94a3b8")),
            margin=dict(l=10, r=60, t=10, b=10), height=380,
        )
        st.plotly_chart(fig_dest, width="stretch", key="t7_dest")
        )
        st.plotly_chart(fig_dest, width="stretch", key="t7_dest")

    st.markdown("---")
    st.markdown("### 🔀 Diagrama de Sankey — Fluxo Origem → Destino (Top 30 fluxos)")
    top30 = df_cruzado.groupby(["municipio_residencia", "municipio_ocorrencia"])["casos"].sum()
    top30 = top30.nlargest(30).reset_index()
    if not top30.empty:
        origens   = top30["municipio_residencia"].unique().tolist()
        destinos  = top30["municipio_ocorrencia"].unique().tolist()
        todos_nos = origens + [d for d in destinos if d not in origens]
        idx = {n: i for i, n in enumerate(todos_nos)}
        fig_sk = go.Figure(go.Sankey(
            node=dict(
                pad=12, thickness=18,
                label=todos_nos,
                color=["#38bdf8" if n in origens else "#fb923c" for n in todos_nos],
            ),
            link=dict(
                source=[idx[r] for r in top30["municipio_residencia"]],
                target=[idx[o] for o in top30["municipio_ocorrencia"]],
                value=top30["casos"].tolist(),
                color="rgba(56,189,248,0.25)",
            )
        ))
        fig_sk.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#f1f5f9", size=18),
            margin=dict(l=10, r=10, t=10, b=10), height=600,
        )
        st.plotly_chart(fig_sk, width="stretch", key="t7_sk")
    else:
        st.info("Sem dados de fluxo disponíveis.")
