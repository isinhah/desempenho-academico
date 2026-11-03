from math import isclose


def _classificar_score(score: float) -> str:
    if score >= 80:
        return "A"
    if score >= 60:
        return "B"
    return "D"


def calcular_score_simples(nota_financeira: float, nota_academica: float) -> dict:
    score = (nota_financeira * 0.60) + (nota_academica * 0.40)
    return {"score": round(score, 2), "classe": _classificar_score(score)}


def validar_pesos(dimensoes: dict) -> bool:
    """Confirma que os pesos das dimensões e indicadores totalizam 100%."""
    if not dimensoes:
        return False

    soma_dimensoes = sum(dimensao["peso_dimensao"] for dimensao in dimensoes.values())
    if not isclose(soma_dimensoes, 1.0, abs_tol=0.000001):
        return False

    for dimensao in dimensoes.values():
        indicadores = dimensao["indicadores"]
        if not indicadores:
            return False
        soma_indicadores = sum(indicador["peso_indicador"] for indicador in indicadores)
        if not isclose(soma_indicadores, 1.0, abs_tol=0.000001):
            return False

    return True


def calcular_score_com_peso_efetivo(dimensoes: dict) -> dict:
    """Calcula o score com peso efetivo de cada indicador."""
    if not validar_pesos(dimensoes):
        raise ValueError("Soma de pesos inválida — deve fechar em 100%.")

    score_total = 0.0
    for dimensao in dimensoes.values():
        for indicador in dimensao["indicadores"]:
            valor = indicador["valor"]
            if not 0 <= valor <= 100:
                raise ValueError("O valor de cada indicador deve estar entre 0 e 100.")
            peso_efetivo = dimensao["peso_dimensao"] * indicador["peso_indicador"]
            score_total += valor * peso_efetivo

    return {
        "score": round(score_total, 2),
        "classe": _classificar_score(score_total),
    }


def calcular_score_por_evasao(pct_evasao: float) -> dict:
    nota_academica = max(0.0, 100 - (pct_evasao * 2))
    dimensoes = {
        "financeiro": {
            "peso_dimensao": 0.55,
            "indicadores": [
                {"nome": "pct_rb_rol", "valor": 85, "peso_indicador": 0.70},
                {"nome": "pct_gp_rol", "valor": 75, "peso_indicador": 0.30},
            ],
        },
        "academico": {
            "peso_dimensao": 0.45,
            "indicadores": [
                {
                    "nome": "pct_evasao_invertido",
                    "valor": nota_academica,
                    "peso_indicador": 1.0,
                }
            ],
        },
    }
    return calcular_score_com_peso_efetivo(dimensoes)
