# Roteiro do vídeo (até 5 minutos)

Grave a tela com OBS ou com a gravação de tela do sistema. Deixe três janelas prontas: o app,
o VS Code e o README. Ensaie uma vez com cronômetro.

| Tempo | Bloco | O que mostrar / falar |
|-------|-------|-----------------------|
| 0:00–0:40 | **Problema e público** | "Em SP, só no 1º semestre de 2026 foram quase 52 mil pedidos de tapa-buraco, cerca de 287 por dia. Quem sofre é quem anda a pé, cadeirante, idoso, morador da periferia. O cidadão não sabe para quem reclamar nem quão grave é." Cite os ODS 11 e 16. |
| 0:40–2:10 | **Demo ponta a ponta** | 1) Use o exemplo "Calçada sem rampa" e mostre que a validação bloqueia texto curto. 2) Clique em Analisar e mostre o status de carregamento (**latência**). 3) Leia a resposta: tipo, urgência com cor + ícone + texto, órgão, orientações. 4) **Human-in-the-loop**: clique em "Quero corrigir", mude a urgência e confirme. 5) Mostre o protocolo e o botão 🔊 Ouvir. 6) Dê 👍 no feedback. |
| 2:10–2:40 | **Gráfico e filtros** | No Painel, mude o período, o tipo e a urgência e mostre o mapa e o hover/zoom do Plotly. Comente o indicador "Correções humanas da IA". |
| 2:40–3:00 | **Cenário de erro** | Pare a API (Ctrl+C no terminal do uvicorn) e tente analisar: aparece a mensagem amigável, sem stack trace, e o texto continua no formulário. Suba a API de novo. |
| 3:00–3:15 | **Gestor (RBAC)** | Entre como Gestor, veja a fila ordenada por urgência e mude a situação para "Encaminhado". |
| 3:15–4:20 | **Código (prova de autoria)** | Árvore de pastas (`features/ui/state/providers` e `routers/schemas/pipelines/providers`). Abra `backend/app/providers/llm.py`, **onde ocorre a chamada ao LLM** com `responses.parse(text_format=AnaliseLLM)`. Abra `schemas/relato.py` (saída Pydantic). Abra `pipelines/regras.py`: órgão e prazo vêm de tabela, não da IA. Abra `frontend/state/sessao.py` (**estado**) e `providers/api_client.py` (`@st.cache_resource` e `@st.cache_data`, **cache**). Mostre `.gitignore` + `.env.example`: a **chave** só existe no back-end, por variável de ambiente. |
| 4:20–5:00 | **Validação e aprendizado** | Mostre a tabela dos testes com pessoas e o ajuste feito. Mostre a tabela dos casos da IA, incluindo o erro real do prompt v1.3 (fio caído → "outros") e a correção na v1.4, que levou a 8/8. Rode `pytest` (36 testes passando). Encerre com o impacto esperado. |

**Dica:** quem fala no vídeo deve ser quem entende o código. O professor usa essa parte para
confirmar a autoria.
