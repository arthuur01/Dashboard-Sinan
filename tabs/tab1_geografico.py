import streamlit as st
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium


def render(df_raw, gdf, anos_sel, tipo_mapa, get_gdf_merged, top10, evolucao_total):
    gdf_merged, df_agg, geo_iface = get_gdf_merged(tuple(sorted(anos_sel)), df_raw, gdf)
    df_top       = top10(df_agg)
    df_evolucao  = evolucao_total(df_raw)
    total_geral  = int(df_agg["total_acidentes"].sum())
    muns_afet    = int((df_agg["total_acidentes"] > 0).sum())
    municipio_top = df_top.iloc[0]["municipio_original"] if len(df_top) > 0 else "-"
    top_valor     = int(df_top.iloc[0]["total_acidentes"]) if len(df_top) > 0 else 0

    st.markdown("## Densidade de casos por município")
    st.markdown("")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value">{total_geral:,}</div>
            <div class="metric-label">Total de Casos no Período</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value">{muns_afet}</div>
            <div class="metric-label">Municípios com Registros</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value" style="font-size:1.2rem">{municipio_top}</div>
            <div class="metric-label">Município com Mais Casos</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value">{top_valor:,}</div>
            <div class="metric-label">Casos no Município Líder</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col_mapa, col_rank = st.columns([3, 2])

    with col_mapa:
        st.markdown("### 🗺️ Mapa de Densidade")
        m = folium.Map(location=[-18.5, -44.5], zoom_start=6, tiles="CartoDB dark_matter")
        if gdf is not None:
            if "Choropleth" in tipo_mapa:
                folium.Choropleth(
                    geo_data=geo_iface,
                    data=gdf_merged,
                    columns=["municipio", "total_acidentes"],
                    key_on="feature.properties.municipio",
                    fill_color="YlOrRd",
                    fill_opacity=0.8,
                    line_opacity=0.2,
                    legend_name="Total de Casos",
                    nan_fill_color="#1a1a2e",
                ).add_to(m)
                folium.GeoJson(
                    geo_iface,
                    style_function=lambda x: {"fillOpacity": 0, "weight": 0},
                    tooltip=folium.GeoJsonTooltip(
                        fields=["municipio", "total_acidentes"],
                        aliases=["Município:", "Casos:"],
                        localize=True,
                        style="background-color:#1e293b;color:#f1f5f9;border:none;"
                    )
                ).add_to(m)
            else:
                from folium.plugins import HeatMap
                heat_data = gdf_merged[gdf_merged["total_acidentes"] > 0][
                    ["centroid_lat", "centroid_lon", "total_acidentes"]
                ].values.tolist()
                HeatMap(heat_data, radius=18, blur=25, max_zoom=10,
                        gradient={0.2: "blue", 0.5: "orange", 1.0: "red"}).add_to(m)
        else:
            st.warning("⚠️ GeoJSON não encontrado em `data/mg_municipios.geojson`.")
        st_folium(m, width="100%", height=500)

    with col_rank:
        st.markdown("### 🏆 Top 10 Municípios")
        cores = ["#f97316","#fb923c","#fdba74","#fed7aa",
                 "#fde68a","#fef08a","#d9f99d","#bbf7d0","#a5f3fc","#bae6fd"]
        fig = go.Figure(go.Bar(
            x=df_top["total_acidentes"],
            y=df_top["municipio_original"],
            orientation="h",
            marker=dict(color=cores[:len(df_top)], line=dict(width=0)),
            text=df_top["total_acidentes"].apply(lambda x: f"{x:,}"),
            textposition="outside",
            textfont=dict(color="#f1f5f9", size=20)
        ))
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            yaxis=dict(categoryorder="total ascending", tickfont=dict(color="#cbd5e1", size=22), title_text="Município", title_font=dict(color="#94a3b8")),
            xaxis=dict(tickfont=dict(color="#64748b"), gridcolor="#1e293b", showgrid=True, title_text="Total de Casos", title_font=dict(color="#94a3b8")),
            margin=dict(l=10, r=60, t=10, b=10), height=460
        )
        st.plotly_chart(fig, width="stretch", key="t1_fig")

    st.markdown("---")
    st.markdown("### 📈 Evolução Temporal de Casos em MG")
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=df_evolucao["ano"], y=df_evolucao["total_acidentes"],
        mode="lines+markers+text",
        line=dict(color="#f97316", width=3),
        marker=dict(size=10, color="#f97316", line=dict(color="#fff", width=2)),
        text=df_evolucao["total_acidentes"].apply(lambda x: f"{x:,}"),
        textposition="top center", textfont=dict(color="#f1f5f9", size=18),
        fill="tozeroy", fillcolor="rgba(249,115,22,0.1)"
    ))
    fig2.update_layout(
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(tickfont=dict(color="#cbd5e1"), gridcolor="#1e293b", dtick=1, title_text="Ano", title_font=dict(color="#94a3b8")),
        yaxis=dict(tickfont=dict(color="#64748b"), gridcolor="#1e293b", title_text="Total de Casos", title_font=dict(color="#94a3b8")),
        margin=dict(l=10, r=10, t=10, b=10), height=280
    )
    st.plotly_chart(fig2, width="stretch", key="t1_fig2")

    st.markdown("---")
    st.markdown("### 📋 Tabela Completa — Todos os Municípios")
    df_tabela = df_agg[df_agg["total_acidentes"] > 0][
        ["ranking", "municipio_original", "codigo_ibge", "total_acidentes"]
    ].rename(columns={
        "ranking": "Ranking", "municipio_original": "Município",
        "codigo_ibge": "Código IBGE", "total_acidentes": "Total de Casos"
    })
    st.dataframe(df_tabela, width="stretch", hide_index=True,
                 column_config={
                     "Ranking": st.column_config.NumberColumn(width="small"),
                     "Total de Casos": st.column_config.ProgressColumn(
                         min_value=0, max_value=int(df_tabela["Total de Casos"].max()), format="%d"
                     )
                 })
