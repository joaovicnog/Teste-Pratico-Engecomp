from extracao import processar_faturas

def aplicar_acrescimo():
    faturas = processar_faturas()

    regras = []

    for fatura in faturas:
        perdas_trans = {"arquivo": fatura["arquivo"], "consumo_ajustado_kwh": None}
        if fatura["distribuidora"] == "CIA LUZ DO VALE" or fatura["distribuidora"] == "COMPANHIA ELETRICA SUDESTE":
            perda_kwh = fatura["consumo_kwh"] * (1 / 100)
            consumo_ajustado_kwh = fatura["consumo_kwh"] + perda_kwh
            ajuste_arredondado = round(consumo_ajustado_kwh, 2)
            perdas_trans["consumo_ajustado_kwh"] = ajuste_arredondado
            regras.append(perdas_trans)

    return regras

if __name__ == "__main__":
    aplicar_acrescimo()