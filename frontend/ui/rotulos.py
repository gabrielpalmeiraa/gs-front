"""Rótulos em linguagem simples e cores semânticas (fonte única da verdade)."""

CATEGORIAS = {
    "buraco_pavimentacao": ("🕳️", "Buraco / asfalto"),
    "iluminacao_publica": ("💡", "Iluminação pública"),
    "calcada_acessibilidade": ("♿", "Calçada / acessibilidade"),
    "alagamento_drenagem": ("🌧️", "Alagamento / bueiro"),
    "lixo_entulho": ("🗑️", "Lixo / entulho"),
    "arvore_poda": ("🌳", "Árvore / poda"),
    "sinalizacao_transito": ("🚦", "Sinalização / semáforo"),
    "outros": ("📌", "Outros"),
}

# Cores escolhidas para contraste ≥ 4.5:1 com texto branco (WCAG AA).
# Cada nível também tem ÍCONE e TEXTO: a informação nunca depende só da cor.
URGENCIAS = {
    "critica": {"icone": "⛔", "rotulo": "Crítica", "cor": "#B3261E", "descricao": "Risco imediato"},
    "alta": {"icone": "⚠️", "rotulo": "Alta", "cor": "#B54708", "descricao": "Resolver em poucos dias"},
    "media": {"icone": "🔶", "rotulo": "Média", "cor": "#8A5A00", "descricao": "Atrapalha a rotina"},
    "baixa": {"icone": "✅", "rotulo": "Baixa", "cor": "#1E7B34", "descricao": "Pequeno incômodo"},
}
ORDEM_URGENCIA = ["critica", "alta", "media", "baixa"]

STATUS = {
    "recebido": ("📥", "Recebido"),
    "em_analise": ("🔎", "Em análise"),
    "encaminhado": ("🚚", "Encaminhado à equipe"),
    "resolvido": ("✔️", "Resolvido"),
    "rejeitado": ("✖️", "Não procede"),
}


def rotulo_categoria(chave: str) -> str:
    icone, nome = CATEGORIAS.get(chave, ("📌", chave))
    return f"{icone} {nome}"


def rotulo_urgencia(chave: str) -> str:
    u = URGENCIAS.get(chave)
    return f"{u['icone']} {u['rotulo']}" if u else chave


def rotulo_status(chave: str) -> str:
    icone, nome = STATUS.get(chave, ("", chave))
    return f"{icone} {nome}"


MAPA_CORES_URGENCIA = {URGENCIAS[k]["rotulo"]: URGENCIAS[k]["cor"] for k in ORDEM_URGENCIA}
