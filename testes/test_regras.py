from extracao import processar_faturas
from regras import aplicar_acrescimo

def test_acrescimo_nas_duas_distribuidoras():
    faturas = processar_faturas()
    resultado = aplicar_acrescimo(faturas)
    arquivos = {r["arquivo"] for r in resultado}
    assert arquivos == {"fatura_02", "fatura_03"}

def test_valor_do_acrescimo():
    faturas = processar_faturas()
    ajustes = {r["arquivo"]: r["consumo_ajustado_kwh"] for r in aplicar_acrescimo(faturas)}
    assert ajustes["fatura_02"] == 4827.8
    assert ajustes["fatura_03"] == 1287.75