import json
import subprocess
import sys
from pathlib import Path

def rodar_solucao():
    Path("resultado.json").unlink(missing_ok=True)
    return subprocess.run([sys.executable, "solucao.py"], capture_output=True, text=True)

def ler_resultado():
    with open("resultado.json", encoding="utf-8") as arquivo:
        faturas = json.load(arquivo)
    return {fatura["arquivo"]: fatura for fatura in faturas}

def test_json_tem_4_faturas():
    rodar_solucao()
    faturas = ler_resultado()
    assert len(faturas) == 4

def test_json_tem_consumo_ajustado():
    rodar_solucao()
    faturas = ler_resultado()
    assert faturas["fatura_02"]["consumo_ajustado_kwh"] == 4827.8
    assert faturas["fatura_03"]["consumo_ajustado_kwh"] == 1287.75
    assert "consumo_ajustado_kwh" not in faturas["fatura_01"]
    assert "consumo_ajustado_kwh" not in faturas["fatura_04"]

def test_relatorio_mostra_divergencia_da_fatura_04():
    saida = rodar_solucao().stdout
    assert "FATURA: fatura_04" in saida
    assert "R$ 180.00 inferior" in saida