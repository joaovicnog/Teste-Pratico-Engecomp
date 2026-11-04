from regras import aplicar_acrescimo

def test_acrescimo_so_nas_duas_distribuidoras():
    resultado = aplicar_acrescimo()
    arquivos = {fatura["arquivo"] for fatura in resultado}
    assert arquivos == {"fatura_02", "fatura_03"}

def test_valor_do_acrescimo():
    ajustes = {fatura["arquivo"]: fatura["consumo_ajustado_kwh"] for fatura in aplicar_acrescimo()}
    assert ajustes["fatura_02"] == 4827.8
    assert ajustes["fatura_03"] == 1287.75