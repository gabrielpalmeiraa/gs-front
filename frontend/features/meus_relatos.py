"""Histórico do cidadão nesta sessão (mantido em st.session_state)."""

import pandas as pd
import plotly.express as px
import streamlit as st

from features.relatar import avaliacao_ia
from providers.api_client import ErroAPI, obter_cliente
from state import sessao
from ui.componentes import cartao_relato, estado_vazio, metrica, mostrar_erro
from ui.rotulos import MAPA_CORES_URGENCIA, ORDEM_URGENCIA, URGENCIAS, rotulo_urgencia


def render() -> None:
    st.subheader("📋 Meus relatos")
    historico = sessao.historico()
    if not historico:
        estado_vazio(
            "Você ainda não registrou nenhum relato",
            "Quando você registrar um problema, ele aparece aqui com o número do protocolo e a situação.",
            "📭",
        )
        return

    c1, c2, c3 = st.columns(3)
    with c1:
        metrica("Relatos nesta sessão", len(historico))
    with c2:
        metrica("Urgentes (alta/crítica)", sum(r["urgencia"] in ("alta", "critica") for r in historico))
    with c3:
        metrica("Resolvidos", sum(r.get("status") == "resolvido" for r in historico))

    if st.button("🔄 Atualizar situação dos meus protocolos"):
        try:
            with st.spinner("Consultando a situação…"):
                for r in historico:
                    sessao.atualizar_no_historico(obter_cliente().obter_relato(r["protocolo"]))
            st.toast("Situação atualizada!", icon="✅")
        except ErroAPI as e:
            mostrar_erro(e)

    # Gráfico alimentado pelo histórico guardado no estado da sessão
    if len(historico) >= 1:
        df = pd.DataFrame(historico)
        df["Urgência"] = df["urgencia"].map(lambda u: URGENCIAS[u]["rotulo"])
        contagem = df.groupby("Urgência").size().reindex([URGENCIAS[u]["rotulo"] for u in ORDEM_URGENCIA]).dropna()
        fig = px.bar(
            contagem.reset_index(name="Relatos"), x="Urgência", y="Relatos", color="Urgência", text="Relatos",
            color_discrete_map=MAPA_CORES_URGENCIA, title="Meus relatos por urgência",
        )
        fig.update_layout(showlegend=False, height=260, margin=dict(t=40, b=10, l=10, r=10))
        st.plotly_chart(fig, width="stretch")

    filtro = st.multiselect(
        "Mostrar urgência", ORDEM_URGENCIA, default=ORDEM_URGENCIA, format_func=rotulo_urgencia, key="filtro_meus"
    )
    for relato in [r for r in historico if r["urgencia"] in filtro]:
        cartao_relato(relato, mostrar_orientacoes=True)
        avaliacao_ia(relato["protocolo"], chave="historico")
