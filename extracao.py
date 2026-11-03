import re
import calendar
import locale
from pathlib import Path
from datetime import datetime
from decimal import Decimal

try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.utf8')
except locale.Error:
    locale.setlocale(locale.LC_ALL, 'Portuguese_Brazil.1252')

def procura_item(alvo):
    if item := alvo:
        resposta = item.group(1).strip()
        return resposta
    else:
        return None

def converte_inteiro(valor):
    valor = re.sub(r"\.", "", valor)
    return int(valor)


def processar_faturas():
    caminho = Path("./dados")
    faturas = []

    contador = 0

    for item in caminho.iterdir():
        if item.is_file():
            with open(item, "r", encoding="utf-8") as arquivo:
                faturas.append(
                    {"arquivo": Path(item).stem,
                    "distribuidora": re.sub(r"\s-.*", "", arquivo.readline().replace("*", "").strip()),
                    "cliente": None,
                    "documento": None,
                    "unidade_consumidora": None,
                    "referencia": None,
                    "vencimento": None,
                    "leitura_anterior": None,
                    "leitura_atual": None,
                    "consumo_kwh": None,
                    "bandeira": None,
                    "valor_total": None}
                    )
                
                for line in arquivo:
                    cliente = procura_item(re.search(r"\b(?:cliente|titular|nome|razao.*?social).*?:(.*)", line, re.IGNORECASE))
                    documento = procura_item(re.search(r"\b(?:cpf/cnpj|cnpj/cpf|documento).*?:(.*)", line, re.IGNORECASE))
                    unidade_consumidora = procura_item(re.search(r"\b(?:unidade.*?consumidora|.*?instalacao).*?:(.*)", line, re.IGNORECASE))
                    referencia = procura_item(re.search(r"\b.*?referencia.*?:(.*)", line, re.IGNORECASE))
                    vencimento = procura_item(re.search(r"\b.*?vencimento.*?:(.*)", line, re.IGNORECASE))
                    leitura_anterior = procura_item(re.search(r"\b.*?anterior(?:[-.a-zA-Z:\s])+(.*\d[^\.])", re.sub(r"\b\d{2,}/\d{2,}/\d{4,}\b", "", line), re.IGNORECASE))
                    leitura_atual = procura_item(re.search(r"\b.*?atual(?:[-.a-zA-Z:\s])+(.*\d[^\.])", re.sub(r"\b\d{2,}/\d{2,}/\d{4,}\b", "", line), re.IGNORECASE))
                    consumo_kwh = procura_item(re.search(r"\b.*?consumo(?:[-.a-zA-Z:\s])(?!.*TUSD|TE)(?:[-.a-zA-Z:\s])+(.*\d[^\.])", line, re.IGNORECASE))
                    bandeira = procura_item(re.search(r"\b.*?bandeira.*?:(.*)", line, re.IGNORECASE))
                    valor_total = procura_item(re.search(r"\b.*?total(?:[-.a-zA-Z:$\s])+(.*)", line, re.IGNORECASE))

                    if cliente:
                        faturas[contador]["cliente"] = cliente

                    if documento:
                        faturas[contador]["documento"] = documento

                    if unidade_consumidora:
                        faturas[contador]["unidade_consumidora"] = unidade_consumidora

                    if cliente:
                        faturas[contador]["cliente"] = cliente

                    if bandeira:
                        faturas[contador]["bandeira"] = bandeira
                    
                    if referencia:
                        for mes_abr, mes_nome in zip(list(calendar.month_abbr)[1:], list(calendar.month_name)[1:]):
                            mes_textual = re.search(r'[a-zA-ZÀ-ÿ]+', referencia)
                            if mes_textual:
                                mes_textual = mes_textual.group()
                                if mes_nome.lower() == mes_textual.lower():
                                    referencia = referencia.replace(mes_textual, str(list(calendar.month_name).index(mes_nome)))
                                if mes_abr.lower() == mes_textual.lower():
                                    referencia = referencia.replace(mes_textual, str(list(calendar.month_abbr).index(mes_abr)))

                        ref_original = datetime.strptime(referencia, "%m/%Y")
                        referencia = ref_original.strftime("%Y-%m")
                        faturas[contador]["referencia"] = referencia
                        
                    if vencimento:
                        vencimento_original = datetime.strptime(vencimento, "%d/%m/%Y")
                        vencimento = vencimento_original.strftime("%Y-%m-%d")
                        faturas[contador]["vencimento"] = vencimento

                    if leitura_anterior:
                        leitura_anterior = converte_inteiro(leitura_anterior)
                        faturas[contador]["leitura_anterior"] = leitura_anterior
                    
                    if leitura_atual:
                        leitura_atual = converte_inteiro(leitura_atual)
                        faturas[contador]["leitura_atual"] = leitura_atual

                    if consumo_kwh:
                        consumo_kwh = converte_inteiro(consumo_kwh)
                        faturas[contador]["consumo_kwh"] = consumo_kwh

                    if valor_total:
                        valor_total = valor_total.replace(".", "")
                        valor_total = valor_total.replace(",", ".")
                        valor_total = Decimal(valor_total)
                        faturas[contador]["valor_total"] = valor_total

        contador += 1

    return faturas