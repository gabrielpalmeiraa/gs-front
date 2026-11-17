"""Identidade visual e ajustes de acessibilidade (alto contraste, fonte maior, foco visível)."""

import streamlit as st

_BASE = """
<style>
  .zelo-badge {display:inline-block;color:#fff;font-weight:700;padding:3px 10px;border-radius:999px;
               font-size:0.9rem;line-height:1.4;white-space:nowrap}
  .zelo-badge--grande {font-size:1.05rem;padding:6px 14px}
  .zelo-vazio {text-align:center;padding:28px 16px;border:2px dashed #94A3B8;border-radius:12px;color:inherit}
  .zelo-vazio__icone {font-size:2.2rem}
  .zelo-hero {padding:4px 0 8px 0}
  .zelo-hero h1 {margin-bottom:0}
  .zelo-protocolo {font-size:2rem;font-weight:800;letter-spacing:1px}
  /* Foco sempre visível para quem navega pelo teclado (WCAG 2.4.7) */
  button:focus-visible, input:focus-visible, textarea:focus-visible, [role="tab"]:focus-visible,
  [data-baseweb="select"] *:focus-visible {outline:3px solid #1D4ED8 !important; outline-offset:2px}
</style>
"""

_FONTE_GRANDE = """
<style>
  html, body, [class*="st-"], .stMarkdown p, label, input, textarea {font-size:1.15rem !important}
  .zelo-badge {font-size:1.05rem}
</style>
"""

_ALTO_CONTRASTE = """
<style>
  .stApp {background:#000 !important; color:#fff !important}
  .stApp p, .stApp label, .stApp span, .stApp h1, .stApp h2, .stApp h3, .stApp li, .stApp div {color:#fff !important}
  .stApp [data-testid="stSidebar"] {background:#000 !important; border-right:2px solid #FFD400}
  .stApp a {color:#FFD400 !important; text-decoration:underline}
  .stApp button {border:2px solid #FFD400 !important}
  .stApp textarea, .stApp input {background:#000 !important; color:#fff !important; border:2px solid #fff !important}
  .zelo-badge {outline:2px solid #fff}
  .zelo-vazio {border-color:#fff}
</style>
"""


def aplicar_tema(alto_contraste: bool, fonte_grande: bool) -> None:
    st.markdown(_BASE, unsafe_allow_html=True)
    if fonte_grande:
        st.markdown(_FONTE_GRANDE, unsafe_allow_html=True)
    if alto_contraste:
        st.markdown(_ALTO_CONTRASTE, unsafe_allow_html=True)
