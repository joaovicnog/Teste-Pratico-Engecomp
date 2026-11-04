from decimal import Decimal
from conferencia import executar_verificacao

def test_so_fatura_04_tem_problema():
    relatorio = executar_verificacao()
    assert len(relatorio) == 1
    assert relatorio[0]["arquivo"] == "fatura_04"

def test_divergencia_fatura_04():
    problema = executar_verificacao()[0]
    assert problema["divergencia"] == Decimal("180.00")
    assert problema["problema"] == "inferior"

def test_campo_ausente_fatura_04():
    problema = executar_verificacao()[0]
    assert problema["ausente"] == ["bandeira"]