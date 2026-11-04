from decimal import Decimal
from conferencia import executar_verificacao
from extracao import processar_faturas

def test_so_fatura_04_tem_problema():
    faturas = processar_faturas()
    relatorio = executar_verificacao(faturas)
    assert len(relatorio) == 1
    assert relatorio[0]["arquivo"] == "fatura_04"

def test_divergencia_fatura_04():
    faturas = processar_faturas()
    problema = executar_verificacao(faturas)[0]
    assert problema["divergencia"] == Decimal("180.00")
    assert problema["problema"] == "inferior"

def test_campo_ausente_fatura_04():
    faturas = processar_faturas()
    problema = executar_verificacao(faturas)[0]
    assert problema["ausente"] == ["bandeira"]