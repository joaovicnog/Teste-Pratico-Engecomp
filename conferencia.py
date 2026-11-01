import re
from extracao import processar_faturas, procura_item
from pathlib import Path
from decimal import Decimal

def executar_verificacao():
    faturas = processar_faturas()
    caminho = Path("./dados")

    divergencia = []
    coerencia = []
    campos_ausentes = []
    conferencia = []

    for fatura in faturas:
        inconsistencia_leitura = {"arquivo": fatura["arquivo"], "incoerencia": None, "leitura_erronea": ""}
        ausencia = {"arquivo": fatura["arquivo"], "ausente": [chave for chave, valor in fatura.items() if valor is None]}
        leitura = fatura["leitura_atual"] - fatura["leitura_anterior"]
        consumo = fatura["consumo_kwh"]
        if consumo > leitura:
            inconsistencia_leitura["incoerencia"] = leitura - consumo
            inconsistencia_leitura["leitura_erronea"] = "superior"
            coerencia.append(inconsistencia_leitura)
        if leitura > consumo:
            inconsistencia_leitura["incoerencia"] = consumo - leitura
            inconsistencia_leitura["leitura_erronea"] = "inferior"
            coerencia.append(inconsistencia_leitura)
        campos_ausentes.append(ausencia)

    contador = 0
    for item in caminho.iterdir():
        contas = []
        if item.is_file():
            with open(item, "r", encoding="utf-8") as arquivo:
                for line in arquivo:
                    tusd = procura_item(re.search(r"\b.*?consumo.*?tusd.*?[\d.]+.*?([\d.,]+)", line, re.IGNORECASE))
                    te = procura_item(re.search(r"\b.*?consumo.*?te.*?[\d.]+.*?([\d.,]+)", line, re.IGNORECASE))
                    bandeira = procura_item(re.search(r"\b.*?bandeira.*?(?![\d%]+)\b(\d[\d.,]+)\b", line, re.IGNORECASE))
                    icms = procura_item(re.search(r"\b.*?icms.*?\b(\d[\d.,]+)\b", re.sub(r"\d+(?:.,\d+)?\s*%", "", line), re.IGNORECASE))
                    pis = procura_item(re.search(r"\b.*?(?:pis|pasep).*?\b(\d[\d.,]+)\b", re.sub(r"\d+(?:.,\d+)?\s*%", "", line), re.IGNORECASE))
                    cofins = procura_item(re.search(r"\b.*?cofins.*?\b(\d[\d.,]+)\b", re.sub(r"\d+(?:.,\d+)?\s*%", "", line), re.IGNORECASE))
                    energia_ativa = procura_item(re.search(r"\b.*?ativa.*?(?!\.)+([\d.,]+)", line, re.IGNORECASE))
                    sistema_de_dist = procura_item(re.search(r"\b.*?sistema.*?(?!\.)+([\d.,]+)", line, re.IGNORECASE))
                    iluminacao = procura_item(re.search(r"\b.*?iluminacao.*?(?!\.)+([\d.,]+)", line, re.IGNORECASE))
                    
                    for tarifa in [tusd, te, bandeira, icms, pis, cofins, energia_ativa, sistema_de_dist, iluminacao]:
                        if tarifa:
                            tarifa = tarifa.replace(".", "")
                            tarifa = tarifa.replace(",", ".")
                            contas.append(Decimal(tarifa))

                soma = sum(contas)
                pago = faturas[contador]["valor_total"]

                diferenca_soma = {"arquivo": faturas[contador]["arquivo"], "divergencia": None, "problema": ""}
                if soma > pago:
                    diferenca_soma["divergencia"] = soma - pago
                    diferenca_soma["problema"] = "superior"
                    divergencia.append(diferenca_soma)
                if pago > soma:
                    diferenca_soma["divergencia"] = pago - soma
                    diferenca_soma["problema"] = "inferior"
                    divergencia.append(diferenca_soma)

        contador += 1
    
    lista_problemas = [divergencia, coerencia, campos_ausentes]
    contador_problemas = 0
    for problema in lista_problemas:
        if problema:
            problema.sort(key=lambda x: x["arquivo"])
            if contador_problemas > 2:
                break
            if contador_problemas == 0:
                for item in problema:
                    conferencia.append(item)
                contador_problemas += 1
            for item in problema:
                contador_arquivo = 0
                while contador_arquivo < len(lista_problemas[contador_problemas]):
                    if item["arquivo"] == lista_problemas[contador_problemas][contador_arquivo]["arquivo"]:
                        for dicio in conferencia:
                            if dicio["arquivo"] == lista_problemas[contador_problemas][contador_arquivo]["arquivo"]:
                                conferencia[conferencia.index(dicio)].update(lista_problemas[contador_problemas][contador_arquivo])
                    contador_arquivo += 1
            contador_problemas += 1

    conferencia.sort(key=lambda x: x['arquivo'])
    
    return conferencia

if __name__ == "__main__":
    executar_verificacao()