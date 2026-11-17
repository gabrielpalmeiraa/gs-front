"""Testes da interface com streamlit.testing (rodam sem navegador e sem back-end)."""

import os
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

APP = str(Path(__file__).resolve().parents[1] / "app.py")


@pytest.fixture
def app_sem_api(monkeypatch):
    # Porta onde nada escuta: simula "API fora do ar".
    monkeypatch.setenv("API_URL", "http://127.0.0.1:9")
    import config, importlib
    importlib.reload(config)
    from providers import api_client
    api_client.obter_cliente.clear()
    api_client.carregar_bairros.clear()
    api_client.carregar_relatos_publicos.clear()
    api_client.verificar_saude.clear()
    return AppTest.from_file(APP, default_timeout=20)


def test_app_abre_sem_excecao_mesmo_com_api_fora(app_sem_api):
    at = app_sem_api.run()
    assert not at.exception
    textos = " ".join(m.value for m in at.markdown)
    assert "Serviço indisponível" in textos


def test_api_fora_mostra_mensagem_amigavel_sem_detalhe_tecnico(app_sem_api):
    at = app_sem_api.run()
    erros = " ".join(e.value for e in at.error)
    assert "Não conseguimos falar com o serviço" in erros
    assert "Traceback" not in erros and "ConnectError" not in erros


def test_validacao_no_front_antes_de_chamar_a_api():
    from features.relatar import validar_entrada

    erros = validar_entrada("buraco", None, "", False)
    assert set(erros) == {"Descrição", "Bairro", "Privacidade"}
    assert validar_entrada("Tem um buraco enorme na rua da escola", "Mooca", "", True) == {}
    assert "Ponto de referência" in validar_entrada("Tem um buraco enorme na rua", "Mooca", "x" * 151, True)
