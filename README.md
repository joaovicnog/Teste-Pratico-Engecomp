## Como rodar

**Requisitos**

- Python 3.12 ou mais recente. O `solucao.py` usa f-strings aninhadas com o mesmo tipo de aspas (ex.: `f"CLIENTE: {fatura["cliente"]}"`), o que só é aceito a partir do 3.12. Em versões anteriores, o programa para com `SyntaxError`.
- Apenas biblioteca padrão: não há nada para instalar.
- Locale pt_BR disponível no sistema. O programa tenta configurar `pt_BR.utf8` e, se não conseguir, `Portuguese_Brazil.1252` (nome usado no Windows). Se nenhuma das duas existir, ele para com `locale.Error`. No Ubuntu, a locale pode ser gerada com `sudo locale-gen pt_BR.UTF-8`.

**Estrutura**

```
.
├── dados/
│   ├── fatura_01.txt
│   ├── fatura_02.txt
│   ├── fatura_03.txt
│   └── fatura_04.txt
├── extracao.py
├── conferencia.py
├── regras.py
└── solucao.py
```

Todo arquivo dentro de `dados/` é lido como fatura, então a pasta deve conter só as faturas.

**Execução**

Na pasta do projeto (a que contém `dados/`):

```bash
python3 solucao.py
```

No Windows: `py solucao.py` ou `python solucao.py`.

O caminho `./dados` é relativo à pasta de onde o comando é executado: rodando de outro diretório, o programa não encontra as faturas e para com `FileNotFoundError`.

**Saída**

1. Um resumo de cada fatura no terminal.
2. O arquivo `resultado.json` gravado na pasta de execução, com os 4 registros.
3. A lista de inconsistências encontradas, no final do terminal.

## Decisões

**Onde está cada responsabilidade**

- `extracao.py` (Módulo 1): lê os arquivos de `dados/` e devolve um dicionário por fatura com os campos do enunciado.
- `conferencia.py` (Módulo 2): faz as três verificações (soma dos itens, coerência da medição e campos ausentes) e devolve os problemas agrupados por fatura.
- `regras.py` (Módulo 3): calcula o consumo ajustado pela perda de transformação.
- `solucao.py`: chama os três módulos, junta os resultados pelo nome do arquivo, imprime o resumo, grava o `resultado.json` e lista as inconsistências.

A conferência e as regras obtêm os dados chamando `processar_faturas()` por conta própria. Os valores dos itens usados na soma (TUSD, TE, tributos etc.) são lidos dos arquivos dentro de `conferencia.py`, já que eles não fazem parte dos campos que o Módulo 1 entrega.

**Extração**

- Em vez de um leitor para cada distribuidora, cada campo tem uma regex que aceita os rótulos dos layouts. Para um layout novo, a ideia é acrescentar os rótulos dele nessas regex.
- A distribuidora é a primeira linha do arquivo, sem os `*` e sem o que vem depois de ` - ` (`*** CIA LUZ DO VALE - DISTRIBUIDORA DE ENERGIA ***` vira `CIA LUZ DO VALE`).
- O documento do cliente só é aceito com os rótulos `CPF/CNPJ`, `CNPJ/CPF` ou `Documento` seguidos de `:`. Como o CNPJ da distribuidora aparece só como `CNPJ`, ele não é capturado.
- Cliente, documento e UC ficam como texto, do jeito que aparecem na fatura (com pontos, barras e hífens).
- Quando o mês de referência vem por extenso (`AGOSTO/2026`), ele é trocado pelo número usando os nomes de mês da locale pt_BR (`calendar.month_name` e `calendar.month_abbr`). É por isso que o programa configura a locale.
- A bandeira vem da linha de resumo com `:` (ex.: `BANDEIRA TARIFARIA VIGENTE: AMARELA`), e não da linha do item cobrado. O texto fica como está na fatura, então a fatura_02 sai como `VERMELHA PATAMAR 1`. Quando essa linha não existe, como na fatura_04, fica `None`.
- Valores em reais vêm no formato brasileiro (`3.461,13`) e são convertidos para `Decimal`, para a soma não ter erro de arredondamento de `float`.

**Conferência**

- A soma considera TUSD, TE, bandeira, ICMS, PIS/PASEP, COFINS, energia ativa, uso do sistema de distribuição e iluminação pública. Nas linhas de ICMS, PIS e COFINS, a porcentagem é removida antes da busca (`ICMS 18,00%`), para a alíquota não ser lida como valor.
- Como os valores são `Decimal`, a comparação com o total é exata: qualquer diferença, inclusive de R$ 0,01, é reportada, indicando se a soma ficou acima (`superior`) ou abaixo (`inferior`) do total declarado.
- Na medição, `superior` indica consumo faturado maior que a diferença entre as leituras, e `inferior`, menor.
- Campo que a regex não encontra fica `None`. Considerei todos os campos obrigatórios, inclusive a bandeira: a fatura_04 fica com `bandeira: None` no JSON, como pede o enunciado, e também aparece com a bandeira na lista de campos ausentes.
- As três verificações geram listas separadas, que depois são agrupadas pelo nome do arquivo, para cada fatura aparecer uma vez só no relatório, com todos os seus problemas juntos.

**Regras e saída**

- O acréscimo de 1% vale quando o nome extraído da distribuidora é exatamente `CIA LUZ DO VALE` ou `COMPANHIA ELETRICA SUDESTE`, e o resultado é arredondado com `round(..., 2)`.
- Só as faturas dessas duas distribuidoras recebem o campo `consumo_ajustado_kwh`, que fica logo depois de `consumo_kwh` (este nunca é alterado). As demais não ganham o campo, em vez de repetir o consumo faturado.
- As inconsistências aparecem só no terminal. O `resultado.json` traz os campos extraídos e o consumo ajustado, com os `Decimal` gravados como número.
- Na Análise comparei o consumo ajustado e para as distribuidoras sem ajuste usei o próprio consumo faturado.

## Análise

**1. Qual unidade consumidora apresentou o maior consumo?**

Ao considerarmos o valor **ajustado** com a perda de transformação:
- Unidade Consumidora: 55-9087341-2
    - Cliente: INDUSTRIA METALURGICA BOA VISTA S/A
    - Distribuidora: CIA LUZ DO VALE
    - Consumo: 4827.8 kWh

## Questionário

Quatro perguntas curtas, também no `README.md`. Responda **com as suas palavras** — queremos a sua
forma de pensar, não a definição de manual.

**2.** Qual foi o desafio mais marcante que você superou no desenvolvimento de uma feature ou
ferramenta?

- Sem dúvida alguma foram estes:
    - Em questão de **complexidade**: Foi encontrar o regex para retornar corretamente cada um dos dados requeridos pelo problema. Presente em `extracao.py` e `conferencia.py`
    - Em questão de **lógica**: Foi implementar o algoritmo que aglutina as diferentes inconsistências em apenas uma lista separada por fatura. Presente em `conferencia.py`

**3.** Quais etapas você costuma seguir quando está incerto sobre um problema?

1. Penso no que faz mais sentido no contexto atual.
2. Busco exemplos de soluções do mesmo problema ou de problemas similares.
3. Testo o método no qual concluí que aparenta fazer mais sentido.
4. Se não der certo, volto a etapa 1.
5. Implemento a solução.

**4.** O que é PEP8?

- Método de estilização de códigos em Python mostrando convenções e padrões para manter o código legível e consistente.

**5.** No Git, o que são conventional commits?

- Commits legíveis de fácil entendimento e que entregam de maneira minimalista e direta a funcionalidade implementada no commit.