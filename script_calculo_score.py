# etapa 1 - peso simples
def calcular_score_simples(nota_financeira: float, nota_academica: float) -> dict:
    peso_financeiro =  0.60 #60%
    peso_academico = 0.40 #40%

    # 1. calculo do score consolidado
    score = (nota_financeira * peso_financeiro) + (nota_academica * peso_academico)

    # 2. faixas de classificação
    # limiares (thresholds) de classificação (são apenas exemplos, o documento não especificou os valores)
    if score >= 80:
        classe = "A"
    elif score >= 60:
        classe = "B"
    else:
        classe = "D"

    return {"score": round(score, 2), "classe": classe}

# teste:
# print(calcular_score_simples(90, 70))

# etapa 2 - peso efetivo

# cada dimensão tem seus dados de peso e indicadores
# a soma dos pesos de todas as dimensões deve dar obrigatoriamente 1.00 (100%)
# a soma dos Indicadores dentro de CADA Dimensão = 100%
dimensoes = {
    "financeiro": {
        "peso_dimensao": 0.65, # peso dessa dimensão dentro do score geral
        "indicadores": [ # lista dos indicadores que compoem essa dimensão
            {"nome": "pct_rb_rol", "valor": 85, "peso_indicador": 0.70}, # indicador 1 com nota x, com x% de peso dentro do financeiro
            {"nome": "pct_gp_rol", "valor": 75, "peso_indicador": 0.30}, # indicador 2 com nota x, com x% de peso dentro do financeiro
        ],
    },
    "academico": {
        "peso_dimensao": 0.35,
        "indicadores": [
            {"nome": "pct_evasao_invertido", "valor": 60, "peso_indicador": 1.0},
        ],
    },
}

# função que confere se os pesos estão corretos antes de calcular
def validar_pesos(dimensoes: dict) -> bool:
    soma_dimensoes = sum(d["peso_dimensao"] for d in dimensoes.values())
    if round(soma_dimensoes, 2) != 1.0:
        return False
    for dim in dimensoes.values():
        soma_indicadores = sum(i["peso_indicador"] for i in dim["indicadores"])
        if round(soma_indicadores, 2) != 1.0:
            return False
    return True

# função principal que calcula o score final do curso
def calcular_score_com_peso_efetivo(dimensoes: dict) -> dict:
    if not validar_pesos(dimensoes):
        raise ValueError("Soma de pesos inválida — deve fechar em 100%")

    score_total = 0
    for dim in dimensoes.values():
        for ind in dim["indicadores"]:
            peso_efetivo = dim["peso_dimensao"] * ind["peso_indicador"]
            score_total += ind["valor"] * peso_efetivo

    classe = "A" if score_total >= 80 else "B" if score_total >= 60 else "D"
    return {"score": round(score_total, 2), "classe": classe}

resultado = calcular_score_com_peso_efetivo(dimensoes)

print(resultado)