"""Componentes visuais reutilizáveis.

Cada função aqui é usada em mais de uma tela ou com parâmetros diferentes
(ex.: `badge_urgencia` aparece no resultado da IA, no histórico, no painel
do gestor e na legenda). Todo texto vindo do usuário ou da IA passa por
`html.escape` antes de ir para HTML, evitando injeção de código (XSS).
"""

import html
import json

import streamlit as st

from providers.api_client import ErroAPI
from ui.rotulos import URGENCIAS, rotulo_categoria, rotulo_status


def badge_urgencia(nivel: str, grande: bool = False) -> str:
    """Retorna HTML de um selo de urgência: cor + ícone + texto + aria-label."""
    u = URGENCIAS.get(nivel)
    if not u:
        return ""
    classe = "zelo-badge zelo-badge--grande" if grande else "zelo-badge"
    rotulo = f"Urgência {u['rotulo']}: {u['descricao']}"
    return (
        f'<span class="{classe}" style="background:{u["cor"]}" role="status" aria-label="{html.escape(rotulo)}">'
        f'{u["icone"]} {u["rotulo"]}{" — " + u["descricao"] if grande else ""}</span>'
    )


def mostrar_badge_urgencia(nivel: str, grande: bool = False) -> None:
    st.markdown(badge_urgencia(nivel, grande), unsafe_allow_html=True)


def cartao_relato(relato: dict, mostrar_descricao: bool = False, mostrar_orientacoes: bool = False) -> None:
    """Cartão de um relato. Usado em 'Meus relatos' (cidadão) e na 'Gestão'."""
    with st.container(border=True):
        col_a, col_b = st.columns([3, 1])
        with col_a:
            st.markdown(
                f"**{html.escape(relato['protocolo'])}** · {rotulo_categoria(relato['categoria'])} · "
                f"{html.escape(relato['bairro'])}"
            )
            st.markdown(html.escape(relato.get("resumo", "")))
        with col_b:
            mostrar_badge_urgencia(relato["urgencia"])
            st.caption(rotulo_status(relato.get("status", "recebido")))
        st.caption(
            f"Responsável: {html.escape(relato.get('orgao_responsavel', '—'))} · "
            f"Prazo de referência: {relato.get('prazo_estimado_dias', '—')} dia(s)"
        )
        if mostrar_descricao and relato.get("descricao_anonimizada"):
            st.markdown("**Relato (dados pessoais já removidos):**")
            st.text(relato["descricao_anonimizada"])
        if mostrar_orientacoes and relato.get("orientacoes_cidadao"):
            with st.expander("O que fazer enquanto isso"):
                for o in relato["orientacoes_cidadao"]:
                    st.markdown(f"- {html.escape(o)}")


def metrica(titulo: str, valor, ajuda: str | None = None, delta: str | None = None) -> None:
    st.metric(titulo, valor, delta=delta, help=ajuda, border=True)


def estado_vazio(titulo: str, texto: str, icone: str = "🗂️") -> None:
    st.markdown(
        f'<div class="zelo-vazio" role="note"><div class="zelo-vazio__icone" aria-hidden="true">{icone}</div>'
        f"<strong>{html.escape(titulo)}</strong><p>{html.escape(texto)}</p></div>",
        unsafe_allow_html=True,
    )


def mostrar_erro(erro: ErroAPI, acao: str | None = None) -> None:
    """Mensagem de erro amigável. Nunca mostra stack trace ao cidadão."""
    texto = f"**{erro.mensagem}**"
    if erro.campos:
        texto += "\n\n" + "\n".join(f"- **{html.escape(c)}**: {html.escape(m)}" for c, m in erro.campos.items())
    if acao:
        texto += f"\n\n{acao}"
    st.error(texto, icon="🚫")


def botao_ouvir(texto: str) -> None:
    """Leitura em voz alta (Web Speech API do navegador, pt-BR). Sem custo e sem dependências."""
    texto_js = html.escape(json.dumps(texto), quote=True)
    st.html(
        f"""
        <button type="button" aria-label="Ouvir as orientações em voz alta"
          onclick="(function(){{const s=window.speechSynthesis;s.cancel();
            const u=new SpeechSynthesisUtterance({texto_js});u.lang='pt-BR';u.rate=0.95;s.speak(u);}})()"
          style="font:600 15px system-ui;padding:8px 14px;border-radius:8px;border:2px solid #1D4ED8;
                 background:#fff;color:#1D4ED8;cursor:pointer">
          🔊 Ouvir orientações
        </button>
        """,
        unsafe_allow_javascript=True,
    )
