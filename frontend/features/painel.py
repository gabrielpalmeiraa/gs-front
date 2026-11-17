"""Painel da cidade: visão agregada e transparente dos relatos (sem dados pessoais)."""

import pandas as pd
import plotly.express as px
import streamlit as st

from providers.api_client import ErroAPI, carregar_relatos_publicos
from ui.componentes import estado_vazio, metrica, mostrar_erro
from ui.rotulos import (
    CATEGORIAS,
    MAPA_CORES_URGENCIA,
    ORDEM_URGENCIA,
    URGENCIAS,
    rotulo_categoria,
    rotulo_status,
    rotulo_urgencia,
)

PERIODOS = {"Últimos 7 dias": 7, "Últimos 15 dias": 15, "Últimos 30 dias": 30, "Tudo": None}


def _preparar(dados: list[dict]) -> pd.DataFrame:
    df = pd.DataFrame(dados)
    df["criado_em"] = pd.to_datetime(df["criado_em"], utc=True, format="ISO8601")
    df["dia"] = df["criado_em"].dt.tz_convert("America/Sao_Paulo").dt.date
    df["Urgência"] = df["urgencia"].map(lambda u: URGENCIAS[u]["rotulo"])
    df["Categoria"] = df["categoria"].map(rotulo_categoria)
    df["Situação"] = df["status"].map(rotulo_status)
    return df


def render() -> None:
    st.subheader("📊 Painel da cidade")
    st.caption("Transparência: todos os relatos confirmados, sem nenhum dado pessoal.")

    # ------------------------------------------------------------ filtros
    with st.container(border=True):
        f1, f2, f3, f4 = st.columns([2, 2, 1.4, 1.2])
        periodo = f1.selectbox("Período", list(PERIODOS), index=2, key="pn_periodo")
        cats = f2.multiselect(
            "Tipo de problema", list(CATEGORIAS), format_func=rotulo_categoria, key="pn_cats",
            placeholder="Todos os tipos",
        )
        urgs = f3.multiselect(
            "Urgência", ORDEM_URGENCIA, format_func=rotulo_urgencia, key="pn_urgs", placeholder="Todas",
        )
        incluir_sim = f4.toggle(
            "Incluir dados simulados", value=True, key="pn_sim",
            help="O painel começa com relatos simulados para demonstração. Desligue para ver só relatos reais.",
        )

    try:
        dados = carregar_relatos_publicos(incluir_sim)
    except ErroAPI as e:
        mostrar_erro(e, "O painel volta assim que o serviço responder.")
        if st.button("Tentar de novo", key="retry_painel"):
            carregar_relatos_publicos.clear()
            st.rerun()
        return

    if not dados:
        estado_vazio("Ainda não há relatos", "Seja a primeira pessoa a relatar um problema na aba 'Relatar'.", "🏙️")
        return

    df = _preparar(dados)
    if PERIODOS[periodo]:
        corte = pd.Timestamp.now(tz="UTC") - pd.Timedelta(days=PERIODOS[periodo])
        df = df[df["criado_em"] >= corte]
    if cats:
        df = df[df["categoria"].isin(cats)]
    if urgs:
        df = df[df["urgencia"].isin(urgs)]

    bairros = sorted(df["bairro"].unique())
    bairro_sel = st.selectbox("Bairro", ["Todos"] + bairros, key="pn_bairro")
    if bairro_sel != "Todos":
        df = df[df["bairro"] == bairro_sel]

    if df.empty:
        estado_vazio("Nenhum relato com esses filtros", "Tente ampliar o período ou remover algum filtro.", "🔍")
        return

    # ---------------------------------------------------------- indicadores
    total = len(df)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metrica("Relatos", total)
    with c2:
        metrica("Críticos", int((df["urgencia"] == "critica").sum()), "Risco imediato à vida ou à integridade física")
    with c3:
        metrica("Resolvidos", f"{(df['status'] == 'resolvido').mean():.0%}")
    with c4:
        metrica(
            "Correções humanas da IA", f"{df['ia_corrigida'].mean():.0%}",
            "Percentual de relatos em que o cidadão corrigiu a classificação da IA (indicador de qualidade da IA).",
        )
    if df["simulado"].any():
        st.caption(f"ℹ️ {int(df['simulado'].sum())} de {total} relatos exibidos são simulados para demonstração.")

    ordem_urg = [URGENCIAS[u]["rotulo"] for u in ORDEM_URGENCIA]
    aba_cat, aba_tempo, aba_mapa, aba_tabela = st.tabs(["Por tipo", "Ao longo do tempo", "Mapa", "Tabela"])

    with aba_cat:
        agrupado = df.groupby(["Categoria", "Urgência"]).size().reset_index(name="Relatos")
        fig = px.bar(
            agrupado, x="Relatos", y="Categoria", color="Urgência", orientation="h",
            pattern_shape="Urgência",  # textura além da cor: acessível para daltônicos
            color_discrete_map=MAPA_CORES_URGENCIA, category_orders={"Urgência": ordem_urg},
            title="Relatos por tipo de problema e urgência",
        )
        fig.update_layout(height=420, yaxis={"categoryorder": "total ascending"}, legend_title_text="Urgência")
        st.plotly_chart(fig, width="stretch")

    with aba_tempo:
        serie = df.groupby(["dia", "Urgência"]).size().reset_index(name="Relatos")
        fig = px.line(
            serie, x="dia", y="Relatos", color="Urgência", markers=True, symbol="Urgência",
            color_discrete_map=MAPA_CORES_URGENCIA, category_orders={"Urgência": ordem_urg},
            title="Relatos por dia", labels={"dia": "Dia"},
        )
        fig.update_layout(height=380, hovermode="x unified")
        st.plotly_chart(fig, width="stretch")

    with aba_mapa:
        fig = px.scatter_map(
            df, lat="latitude", lon="longitude", color="Urgência", color_discrete_map=MAPA_CORES_URGENCIA,
            category_orders={"Urgência": ordem_urg},
            hover_name="protocolo", hover_data={"Categoria": True, "bairro": True, "Situação": True,
                                                "latitude": False, "longitude": False},
            zoom=9.3, height=480, map_style="open-street-map", title="Onde estão os problemas",
        )
        fig.update_traces(marker={"size": 12})
        st.plotly_chart(fig, width="stretch")
        st.caption("Por privacidade, cada ponto fica próximo ao centro do bairro, não no endereço exato.")

    with aba_tabela:
        st.dataframe(
            df.sort_values("criado_em", ascending=False)[
                ["protocolo", "criado_em", "bairro", "Categoria", "Urgência", "Situação", "orgao_responsavel"]
            ].rename(columns={"protocolo": "Protocolo", "criado_em": "Data", "bairro": "Bairro", "orgao_responsavel": "Responsável"}),
            hide_index=True, width="stretch",
        )
