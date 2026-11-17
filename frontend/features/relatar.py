"""Tela principal do cidadão: relatar -> IA analisa -> cidadão confirma/corrige -> protocolo.

Fluxo em 3 etapas controlado por state/sessao.py:
  FORMULARIO  -> entrada validada antes do envio
  REVISAO     -> human-in-the-loop: a IA sugere, o cidadão decide
  CONCLUIDO   -> protocolo + orientações + avaliação
"""

import html
import time

import streamlit as st

from providers.api_client import ErroAPI, carregar_bairros, carregar_relatos_publicos, obter_cliente
from state import sessao
from ui.componentes import botao_ouvir, mostrar_badge_urgencia, mostrar_erro
from ui.rotulos import CATEGORIAS, ORDEM_URGENCIA, rotulo_categoria, rotulo_urgencia

MIN_CARACTERES, MAX_CARACTERES, MAX_REFERENCIA = 20, 1000, 150

EXEMPLOS = {
    "Poste apagado": (
        "O poste da esquina está apagado há uma semana e a rua fica totalmente escura. "
        "Muita gente passa a pé à noite voltando do metrô.",
        "Tatuapé",
        "Saída do metrô Carrão",
    ),
    "Calçada sem rampa": (
        "A calçada em frente à UBS está toda quebrada e sem rampa. Minha mãe é cadeirante e "
        "precisa ir pela rua no meio dos carros para chegar na consulta.",
        "Capão Redondo",
        "Em frente à UBS",
    ),
    "Bueiro entupido": (
        "A boca de lobo da rua está entupida de lixo e toda vez que chove a água entra nas casas.",
        "Jardim Ângela",
        "",
    ),
}


def validar_entrada(descricao: str, bairro: str | None, referencia: str, consentiu: bool) -> dict[str, str]:
    """Validação no front-end, ANTES de gastar uma chamada à IA.
    (O back-end valida de novo com Pydantic: nunca confiamos só no cliente.)"""
    erros: dict[str, str] = {}
    texto = descricao.strip()
    if not texto:
        erros["Descrição"] = "Conte o que está acontecendo."
    elif len(texto) < MIN_CARACTERES or len(texto.split()) < 4:
        erros["Descrição"] = f"Escreva um pouco mais (mínimo de {MIN_CARACTERES} letras e 4 palavras)."
    elif len(texto) > MAX_CARACTERES:
        erros["Descrição"] = f"O texto passou do limite de {MAX_CARACTERES} caracteres."
    if not bairro:
        erros["Bairro"] = "Escolha o bairro onde está o problema."
    if len(referencia.strip()) > MAX_REFERENCIA:
        erros["Ponto de referência"] = f"Use no máximo {MAX_REFERENCIA} caracteres."
    if not consentiu:
        erros["Privacidade"] = "Para continuar, marque que você leu como seus dados são tratados."
    return erros


def _etapas_visuais(atual: int) -> None:
    nomes = ["1. Conte o problema", "2. Confira a análise", "3. Receba o protocolo"]
    partes = [f"**{n}**" if i == atual else f"<span style='opacity:.6'>{n}</span>" for i, n in enumerate(nomes)]
    st.markdown(" → ".join(partes), unsafe_allow_html=True)


# ---------------------------------------------------------------- etapa 1
def _formulario() -> None:
    _etapas_visuais(0)
    try:
        bairros = [b["nome"] for b in carregar_bairros()]
    except ErroAPI as e:
        mostrar_erro(e, "Sem a lista de bairros não conseguimos registrar o relato agora.")
        if st.button("Tentar de novo", key="retry_bairros"):
            carregar_bairros.clear()
            st.rerun()
        return

    with st.expander("💡 Não sabe como escrever? Use um exemplo"):
        cols = st.columns(len(EXEMPLOS))
        for col, (nome, dados) in zip(cols, EXEMPLOS.items()):
            col.button(nome, key=f"ex_{nome}", on_click=sessao.preencher_exemplo, args=dados, width="stretch")

    with st.form("form_relato", clear_on_submit=False, enter_to_submit=False):
        descricao = st.text_area(
            "O que está acontecendo? *",
            key="campo_descricao",
            max_chars=MAX_CARACTERES,
            height=140,
            placeholder="Ex.: Tem um buraco grande na rua em frente à escola e os carros estão desviando pela calçada.",
            help="Conte com suas palavras: o que é, há quanto tempo, se oferece perigo.",
        )
        c1, c2 = st.columns(2)
        bairro = c1.selectbox(
            "Bairro *", bairros, key="campo_bairro", index=None, placeholder="Escolha o bairro",
            help="Usamos o bairro para encaminhar o pedido e consultar a previsão de chuva da região.",
        )
        referencia = c2.text_input(
            "Ponto de referência (opcional)", key="campo_referencia", max_chars=MAX_REFERENCIA,
            placeholder="Ex.: em frente à padaria", help="Não informe seu endereço residencial.",
        )
        consentiu = st.checkbox(
            "Li e concordo: meu relato será analisado por inteligência artificial. "
            "Telefone, CPF, e-mail e placas são removidos automaticamente antes da análise.",
            key="campo_consentimento",
        )
        st.caption("* campos obrigatórios")
        enviado = st.form_submit_button("Analisar meu relato", type="primary", width="stretch")

    if not enviado:
        return

    erros = validar_entrada(descricao, bairro, referencia, consentiu)
    if erros:
        st.error(
            "**Falta pouco! Ajuste os itens abaixo:**\n\n" + "\n".join(f"- **{c}**: {m}" for c, m in erros.items()),
            icon="✏️",
        )
        return

    entrada = {"descricao": descricao.strip(), "bairro": bairro, "referencia": referencia.strip() or None}
    inicio = time.perf_counter()
    # Design para latência: o cidadão vê que algo está acontecendo e por quê.
    with st.status("Analisando seu relato… isso leva alguns segundos.", expanded=True) as status:
        st.write("🔒 Enviando com segurança e removendo dados pessoais")
        st.write("🌦️ Consultando a previsão de chuva do bairro")
        st.write("🤖 Inteligência artificial classificando o problema")
        try:
            analise = obter_cliente().analisar(**entrada)
        except ErroAPI as e:
            status.update(label="Não foi possível analisar agora", state="error", expanded=False)
            mostrar_erro(e, "Seu texto continua salvo no formulário. Você pode tentar de novo.")
            return
        status.update(label=f"Análise pronta em {time.perf_counter() - inicio:.1f} s", state="complete", expanded=False)

    sessao.iniciar_revisao(entrada, analise)
    st.rerun()


# ---------------------------------------------------------------- etapa 2
def _revisao() -> None:
    _etapas_visuais(1)
    analise, entrada = st.session_state.analise_atual, st.session_state.entrada_atual

    if analise["risco_imediato"]:
        st.error(
            "**Possível risco imediato.** Afaste-se do local. Em caso de perigo agora, ligue "
            "**199 (Defesa Civil)** ou **193 (Bombeiros)**.",
            icon="⛔",
        )
    if analise["fora_do_escopo"]:
        st.warning(
            "Este canal é para problemas em ruas, calçadas e espaços públicos. Pelo que entendemos, seu relato "
            "parece ser de outro tipo. Emergências: **190** Polícia · **192** SAMU · **193** Bombeiros.",
            icon="🧭",
        )

    with st.container(border=True):
        st.markdown("#### O que entendemos do seu relato")
        st.markdown(f"> {html.escape(analise['resumo'])}")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("**Tipo de problema**")
            st.markdown(rotulo_categoria(analise["categoria"]))
        with c2:
            st.markdown("**Urgência**")
            mostrar_badge_urgencia(analise["urgencia"], grande=True)
        with c3:
            st.markdown("**Quem resolve**")
            st.markdown(html.escape(analise["orgao_responsavel"]))
        st.markdown(f"**Por que essa urgência?** {html.escape(analise['justificativa_urgencia'])}")
        st.caption(f"Prazo de referência do protótipo: até {analise['prazo_estimado_dias']} dia(s).")

        st.markdown("**O que fazer enquanto isso:**")
        for o in analise["orientacoes_cidadao"]:
            st.markdown(f"- {html.escape(o)}")

        detalhes = []
        if analise.get("dados_pessoais_removidos"):
            detalhes.append("🔒 Para proteger você, removemos do texto: " + ", ".join(analise["dados_pessoais_removidos"]) + ".")
        if analise.get("contexto_clima"):
            cl = analise["contexto_clima"]
            detalhes.append(f"🌦️ Previsão de chuva hoje no bairro: {cl['chuva_prevista_mm']:.1f} mm (fonte: {cl['fonte']}).")
        for ajuste in analise.get("ajustes_por_regra", []):
            detalhes.append(f"📐 {ajuste}")
        for d in detalhes:
            st.caption(d)

    if analise["precisa_revisao_humana"]:
        st.warning(
            "**A IA não teve total certeza. Confira com atenção antes de confirmar:**\n\n"
            + "\n".join(f"- {html.escape(m)}" for m in analise["motivos_revisao"]),
            icon="🧐",
        )

    # ------------------- human-in-the-loop ---------------------------------
    st.markdown("#### A análise está correta?")
    escolha = st.radio(
        "Confirme ou corrija antes de gerar o protocolo",
        ["Sim, está correto", "Quero corrigir"],
        horizontal=True,
        key="hitl_escolha",
        index=1 if analise["precisa_revisao_humana"] else 0,
    )
    categoria_final, urgencia_final = analise["categoria"], analise["urgencia"]
    if escolha == "Quero corrigir":
        c1, c2 = st.columns(2)
        cats = list(CATEGORIAS)
        categoria_final = c1.selectbox(
            "Tipo de problema", cats, index=cats.index(analise["categoria"]), format_func=rotulo_categoria, key="hitl_cat"
        )
        urgencia_final = c2.selectbox(
            "Urgência", ORDEM_URGENCIA, index=ORDEM_URGENCIA.index(analise["urgencia"]), format_func=rotulo_urgencia,
            key="hitl_urg",
        )

    b1, b2, b3 = st.columns([2, 1, 1])
    confirmar = b1.button(
        "✅ Confirmar e gerar protocolo", type="primary", width="stretch", disabled=analise["fora_do_escopo"]
    )
    b2.button("✏️ Editar relato", on_click=sessao.voltar_para_edicao, width="stretch")
    b3.button("Cancelar", on_click=sessao.novo_relato, width="stretch")

    if confirmar:
        with st.spinner("Registrando seu protocolo…"):
            try:
                relato = obter_cliente().confirmar(analise["analise_id"], categoria_final, urgencia_final)
            except ErroAPI as e:
                mostrar_erro(e)
                return
        carregar_relatos_publicos.clear()  # painel precisa refletir o novo relato
        sessao.concluir(relato, analise)
        st.rerun()

    with st.expander("Ver o texto que você enviou"):
        st.text(entrada["descricao"])


# ---------------------------------------------------------------- etapa 3
def _concluido() -> None:
    _etapas_visuais(2)
    relato = st.session_state.relato_confirmado
    st.success("Relato registrado com sucesso!", icon="🎉")
    with st.container(border=True):
        st.markdown("Guarde o número do seu protocolo:")
        st.markdown(f'<div class="zelo-protocolo">{html.escape(relato["protocolo"])}</div>', unsafe_allow_html=True)
        mostrar_badge_urgencia(relato["urgencia"], grande=True)
        st.markdown(
            f"{rotulo_categoria(relato['categoria'])} · {html.escape(relato['bairro'])}  \n"
            f"Encaminhado para: **{html.escape(relato['orgao_responsavel'])}**  \n"
            f"Prazo de referência: **até {relato['prazo_estimado_dias']} dia(s)**"
        )
        if relato.get("ia_corrigida"):
            st.caption("📝 Você corrigiu a análise da IA. Obrigado: isso ajuda a melhorar o sistema.")
        orientacoes = relato.get("orientacoes_cidadao", [])
        if orientacoes:
            st.markdown("**Enquanto isso:**")
            for o in orientacoes:
                st.markdown(f"- {html.escape(o)}")
            botao_ouvir(" ".join(orientacoes))

    avaliacao_ia(relato["protocolo"], chave="concluido")
    st.button("➕ Registrar outro problema", on_click=sessao.novo_relato, type="primary")


def avaliacao_ia(protocolo: str, chave: str) -> None:
    """Segundo ponto de human-in-the-loop: o cidadão avalia a resposta da IA."""
    if sessao.feedback_de(protocolo):
        st.caption("Obrigado pela sua avaliação! 💙")
        return
    st.markdown("**A orientação da IA foi útil?**")
    valor = st.feedback("thumbs", key=f"fb_{chave}_{protocolo}")
    if valor is not None:
        avaliacao = "util" if valor == 1 else "incorreto"
        try:
            obter_cliente().enviar_feedback(protocolo, sessao.comprovante_de(protocolo), avaliacao)
            sessao.registrar_feedback(protocolo, avaliacao)
            carregar_relatos_publicos.clear()
            st.toast("Avaliação registrada. Obrigado!", icon="💙")
        except ErroAPI as e:
            mostrar_erro(e)


def render() -> None:
    st.subheader("📝 Relatar um problema na cidade")
    {sessao.FORMULARIO: _formulario, sessao.REVISAO: _revisao, sessao.CONCLUIDO: _concluido}[sessao.etapa()]()
