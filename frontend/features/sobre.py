"""Como funciona, privacidade e limites da IA, em linguagem simples."""

import streamlit as st

from ui.componentes import badge_urgencia
from ui.rotulos import ORDEM_URGENCIA


def render() -> None:
    st.subheader("ℹ️ Como o Zelo funciona")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(
            """
**Em 3 passos**
1. Você conta o problema com suas palavras.
2. A inteligência artificial sugere o tipo, a urgência e quem resolve. **Você confere e pode corrigir.**
3. Você recebe um protocolo para acompanhar.

**Seus dados**
- Telefone, CPF, e-mail e placas são **apagados automaticamente** antes da análise.
- Não pedimos seu nome nem seu endereço.
- O painel público mostra só o resumo, nunca o seu texto.
"""
        )
    with c2:
        st.markdown(
            """
**O que a IA NÃO faz**
- Não substitui a Defesa Civil, os Bombeiros ou a Polícia.
- Não garante prazo: os prazos mostrados são de referência.
- Pode errar. Por isso, **você sempre confirma** antes de gerar o protocolo, e a equipe da Prefeitura revisa.

**Emergência?** 190 Polícia · 192 SAMU · 193 Bombeiros · 199 Defesa Civil
"""
        )
    st.markdown("**Como lemos a urgência**")
    st.markdown(
        " ".join(badge_urgencia(u, grande=True) for u in ORDEM_URGENCIA),
        unsafe_allow_html=True,
    )
    st.caption("Cada nível tem cor, ícone e nome, para não depender só da cor.")
    with st.expander("Recursos de acessibilidade"):
        st.markdown(
            """
- Alto contraste e fonte maior (barra lateral).
- Leitura em voz alta das orientações.
- Navegação por teclado com foco visível.
- Urgência indicada por cor **e** ícone **e** texto; gráficos com texturas, além de cores.
- Rótulos e textos de ajuda em todos os campos, em linguagem simples.
"""
        )
