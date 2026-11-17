"""Zelo — zeladoria urbana com IA (front-end Streamlit).

Rodar localmente (a partir da pasta frontend/):
    streamlit run app.py

Este arquivo só monta o layout (sidebar + abas). Cada tela vive em features/,
componentes visuais em ui/, estado em state/ e o acesso à API em providers/.
"""

import streamlit as st

st.set_page_config(page_title="Zelo · Zeladoria urbana com IA", page_icon="🏙️", layout="wide")

from features import gestor, meus_relatos, painel, relatar, sobre  # noqa: E402
from providers.api_client import verificar_saude  # noqa: E402
from state import sessao  # noqa: E402
from ui.tema import aplicar_tema  # noqa: E402

sessao.inicializar()

# ------------------------------------------------------------------ sidebar
with st.sidebar:
    st.markdown("## 🏙️ Zelo")
    st.caption("Sua rua, cuidada. Relate problemas da cidade e acompanhe a solução.")

    if verificar_saude():
        st.markdown("🟢 **Serviço online**")
    else:
        st.markdown("🔴 **Serviço indisponível no momento**")
        st.caption("Você ainda pode ver as informações, mas o envio de relatos pode falhar.")

    st.divider()
    st.radio("Entrar como", ["Cidadão", "Gestor"], key="perfil", horizontal=True)
    if st.session_state.perfil == "Gestor":
        with st.form("login_gestor", clear_on_submit=True):
            token = st.text_input("Código de acesso da equipe", type="password")
            if st.form_submit_button("Entrar"):
                st.session_state.gestor_token = token or None
        if st.session_state.gestor_token:
            st.caption("🔓 Acesso de gestor ativo nesta sessão.")
            if st.button("Sair"):
                st.session_state.gestor_token = None
                st.rerun()

    st.divider()
    st.markdown("**Acessibilidade**")
    st.toggle("Alto contraste", key="alto_contraste")
    st.toggle("Fonte maior", key="fonte_grande")

    st.divider()
    st.caption("Emergência: 190 Polícia · 192 SAMU · 193 Bombeiros · 199 Defesa Civil")
    st.caption("Protótipo acadêmico · FIAP Global Solution 2026.2 · CitizenTech")

aplicar_tema(st.session_state.alto_contraste, st.session_state.fonte_grande)

# --------------------------------------------------------------- cabeçalho
st.markdown(
    '<div class="zelo-hero"><h1>Zelo</h1><p>Viu um buraco, um poste apagado ou uma calçada quebrada? '
    "Conte aqui. A IA organiza o pedido, você confere e a Prefeitura recebe tudo pronto para agir.</p></div>",
    unsafe_allow_html=True,
)

# -------------------------------------------------------------------- abas
nomes = ["📝 Relatar", "📋 Meus relatos", "📊 Painel da cidade", "ℹ️ Como funciona"]
telas = [relatar.render, meus_relatos.render, painel.render, sobre.render]
if st.session_state.perfil == "Gestor":
    nomes.insert(3, "🛠️ Gestão")
    telas.insert(3, gestor.render)

for aba, tela in zip(st.tabs(nomes), telas):
    with aba:
        tela()
