import re
import locale
from pathlib import Path
from datetime import datetime
from decimal import Decimal

try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.utf8')
except locale.Error:
    locale.setlocale(locale.LC_ALL, 'Portuguese_Brazil.1252')

MAPA_MESES = {
    re.compile(r'\bjan\w*', re.IGNORECASE): '01',
    re.compile(r'\bfev\w*', re.IGNORECASE): '02',
    re.compile(r'\bmar\w*', re.IGNORECASE): '03',
    re.compile(r'\babr\w*', re.IGNORECASE): '04',
    re.compile(r'\bmai\w*', re.IGNORECASE): '05',
    re.compile(r'\bjun\w*', re.IGNORECASE): '06',
    re.compile(r'\bjul\w*', re.IGNORECASE): '07',
    re.compile(r'\bago\w*', re.IGNORECASE): '08',
    re.compile(r'\bset\w*', re.IGNORECASE): '09',
    re.compile(r'\bout\w*', re.IGNORECASE): '10',
    re.compile(r'\bnov\w*', re.IGNORECASE): '11',
    re.compile(r'\bdez\w*', re.IGNORECASE): '12'
}

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

    for item in caminho.iterdir():
        if item.is_file():
            with open(item, "r", encoding="utf-8") as arquivo:
                fatura_atual = (
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
                    referencia = procura_item(re.search(r"\b.*?refer[eê]ncia.*?:(.*)", line, re.IGNORECASE))
                    vencimento = procura_item(re.search(r"\b.*?vencimento.*?:(.*)", line, re.IGNORECASE))
                    leitura_anterior = procura_item(re.search(r"\b.*?anterior(?:[-.a-zA-Z:\s])+(.*\d[^\.])", re.sub(r"\b\d{2,}/\d{2,}/\d{4,}\b", "", line), re.IGNORECASE))
                    leitura_atual = procura_item(re.search(r"\b.*?atual(?:[-.a-zA-Z:\s])+(.*\d[^\.])", re.sub(r"\b\d{2,}/\d{2,}/\d{4,}\b", "", line), re.IGNORECASE))
                    consumo_kwh = procura_item(re.search(r"\b.*?consumo(?:[-.a-zA-Z:\s])(?!.*TUSD|TE)(?:[-.a-zA-Z:\s])+(.*\d[^\.])", line, re.IGNORECASE))
                    bandeira = procura_item(re.search(r"\b.*?bandeira.*?:(.*)", line, re.IGNORECASE))
                    valor_total = procura_item(re.search(r"\b.*?total(?:[-.a-zA-Z:$\s])+(.*)", line, re.IGNORECASE))

                    if cliente:
                        fatura_atual["cliente"] = cliente

                    if documento:
                        fatura_atual["documento"] = documento

                    if unidade_consumidora:
                        fatura_atual["unidade_consumidora"] = unidade_consumidora

                    if cliente:
                        fatura_atual["cliente"] = cliente

                    if bandeira:
                        fatura_atual["bandeira"] = bandeira

                    if referencia:
                        for padrao, num_mes in MAPA_MESES.items():
                            if padrao.search(referencia):
                                referencia = padrao.sub(num_mes, referencia)
                                break
                        try:
                            ref_original = datetime.strptime(referencia, "%m/%Y")
                            fatura_atual["referencia"] = ref_original.strftime("%Y-%m")
                        except ValueError:
                            pass
                        
                    if vencimento:
                        try:
                            vencimento_original = datetime.strptime(vencimento, "%d/%m/%Y")
                            fatura_atual["vencimento"] = vencimento_original.strftime("%Y-%m-%d")
                        except ValueError:
                            pass

                    if leitura_anterior:
                        leitura_anterior = converte_inteiro(leitura_anterior)
                        fatura_atual["leitura_anterior"] = leitura_anterior
                    
                    if leitura_atual:
                        leitura_atual = converte_inteiro(leitura_atual)
                        fatura_atual["leitura_atual"] = leitura_atual

                    if consumo_kwh:
                        consumo_kwh = converte_inteiro(consumo_kwh)
                        fatura_atual["consumo_kwh"] = consumo_kwh

                    if valor_total:
                        try:
                            valor_limpo = valor_total.replace(".", "").replace(",", ".")
                            fatura_atual["valor_total"] = Decimal(valor_limpo)
                        except Exception:
                            pass

                faturas.append(fatura_atual)

    return faturas

if __name__ == "__main__":
    resultado = processar_faturas()
    print(f"Processadas {len(resultado)} faturas com sucesso.")
    for f in resultado:
        print(f)