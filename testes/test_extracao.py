import re
from decimal import Decimal
import pytest
from extracao import converte_inteiro, procura_item, processar_faturas

def test_converte_inteiro_tira_o_ponto():
    entrada = "28.450"
    resultado = converte_inteiro(entrada)
    assert resultado == 28450

def test_converte_inteiro_recusa_valor_em_reais():
    with pytest.raises(ValueError):
        converte_inteiro("1.492,00")

def test_procura_item_encontrou():
    achado = re.search(r"CLIENTE:(.*)", "CLIENTE:   PADARIA AURORA   ")
    resultado = procura_item(achado)
    assert resultado == "PADARIA AURORA"

def test_procura_item_nao_encontrou():
    achado = re.search(r"CLIENTE:(.*)", "linha sem o campo")
    resultado = procura_item(achado)
    assert resultado is None

def test_processar_faturas_le_4_arquivos():
    faturas = processar_faturas()
    assert len(faturas) == 4

def test_processar_faturas_fatura_02():
    faturas = {fatura["arquivo"]: fatura for fatura in processar_faturas()}
    fatura = faturas["fatura_02"]

    assert fatura["distribuidora"] == "CIA LUZ DO VALE"
    assert fatura["referencia"] == "2026-08"
    assert fatura["vencimento"] == "2026-09-05"
    assert fatura["leitura_anterior"] == 154220
    assert fatura["leitura_atual"] == 159000
    assert fatura["consumo_kwh"] == 4780
    assert fatura["valor_total"] == Decimal("5960.89")

def test_processar_faturas_campo_ausente_none():
    faturas = {f["arquivo"]: f for f in processar_faturas()}
    assert faturas["fatura_04"]["bandeira"] is None