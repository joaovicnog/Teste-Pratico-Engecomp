import json
from extracao import processar_faturas
from conferencia import executar_verificacao
from regras import aplicar_acrescimo

faturas = processar_faturas()
verifica_problemas = executar_verificacao()
aplica_regras = aplicar_acrescimo()

for indice, fatura in enumerate(faturas):
    for regra in aplica_regras:
        if fatura["arquivo"] == regra["arquivo"]:
            fatura.update(regra)
            chaves = list(fatura.keys())
            chaves.remove("consumo_ajustado_kwh")
            indice_alvo = chaves.index("consumo_kwh")
            chaves.insert(indice_alvo + 1, "consumo_ajustado_kwh")
            faturas[indice] = {chave: fatura[chave] for chave in chaves}

for fatura in faturas:
    print(f"""
    =========================================================
                RESUMO - CONTA DE ENERGIA ELETRICA
    =========================================================
    {f"DISTRIBUIDORA: {fatura["distribuidora"]}" if ("distribuidora" in fatura and fatura["distribuidora"] != None) else ""}
    {f"CLIENTE: {fatura["cliente"]}" if ("cliente" in fatura and fatura["cliente"] != None) else ""}
    {f"DOCUMENTO DO CLIENTE: {fatura["documento"]}" if ("documento" in fatura and fatura["documento"] != None) else ""}
    {f"UNIDADE CONSUMIDORA: {fatura["unidade_consumidora"]}" if ("unidade_consumidora" in fatura and fatura["unidade_consumidora"] != None) else ""}

    {f"MES DE COMPETENCIA: {fatura["referencia"]}" if ("referencia" in fatura and fatura["referencia"] != None) else ""}
    {f"DATA DE VENCIMENTO: {fatura["vencimento"]}" if ("vencimento" in fatura and fatura["vencimento"] != None) else ""}

    ---------------------------------------------------------
    MEDICAO
    ---------------------------------------------------------
    {f"LEITURA ANTERIOR ....... {fatura["leitura_anterior"]}\tkWh" if ("leitura_anterior" in fatura and fatura["leitura_anterior"] != None) else ""}
    {f"LEITURA ATUAL .......... {fatura["leitura_atual"]}\tkWh" if ("leitura_atual" in fatura and fatura["leitura_atual"] != None) else ""}
    {f"CONSUMO FATURADO ....... {fatura["consumo_kwh"]}\tkWh" if ("consumo_kwh" in fatura and fatura["consumo_kwh"] != None) else ""}
    {f"""
    ---------------------------------------------------------
    PERDAS DE TRANSFORMACAO
    ---------------------------------------------------------
    CONSUMO AJUSTADO ....... {fatura["consumo_ajustado_kwh"]} kWh
    """ if ("consumo_ajustado_kwh" in fatura and fatura["consumo_ajustado_kwh"] != None) else ""
    }
    ---------------------------------------------------------
    FATURAMENTO DECLARADO
    ---------------------------------------------------------
    {f"VALOR TOTAL NA FATURA:    R$\t{fatura["valor_total"]}" if ("valor_total" in fatura and fatura["valor_total"] != None) else ""}
    =========================================================
    {f"BANDEIRA TARIFARIA VIGENTE: {fatura["bandeira"]}" if ("bandeira" in fatura and fatura["bandeira"] != None) else ""}
    """)

with open("resultado.json", "w", encoding="utf-8") as saida_json:
    json.dump(faturas, saida_json, default=float)


print("""
    ---------------------------------------------------------
                 INCONSISTENCIAS ENCONTRADAS
    ---------------------------------------------------------
""")
for problema in verifica_problemas:
    print(f"""
    {f"FATURA: {problema["arquivo"]}" if ("arquivo" in problema and problema["arquivo"] != None) else ""}
    PROBLEMAS:
    {f"""\t- A fatura ({problema["arquivo"]}) constatou um valor de
    \tR$ {problema["divergencia"]} {problema["problema"]} ao seu valor real."""
     if ("divergencia" in problema and problema["divergencia"] != None) else ""
     }
    {f"""\t- A fatura ({problema["arquivo"]}) constatou um consumo de
    \t{problema["inconsistencia"]} kWh {problema["leitura_erronea"]} ao seu valor real."""
     if ("inconsistencia" in problema and problema["inconsistencia"] != None) else ""
     }
    {f"""\t- A fatura ({problema["arquivo"]}) nao forneceu dados de
    \t{', '.join(problema["ausente"])}"""
     if ("ausente" in problema and problema["ausente"] != None) else ""
     }
    """)