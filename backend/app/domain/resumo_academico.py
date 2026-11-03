from datetime import date

from app.domain.calculo_score import calcular_score_por_evasao


def _formatar_percentual(valor: float) -> str:
    return f"{valor:.2f}%".replace(".", ",")


def gerar_resumo_academico(historico: list[tuple[date, float]]) -> str | None:
    if not historico:
        return None

    ordenado = sorted(historico, key=lambda indicador: indicador[0])
    evasao_atual = float(ordenado[-1][1])
    score = calcular_score_por_evasao(evasao_atual)
    sufixo_score = (
        f"O score atual é {score['score']:.2f}".replace(".", ",")
        + f", na Classe {score['classe']}."
    )

    if len(ordenado) == 1:
        return f"A evasão mais recente é {_formatar_percentual(evasao_atual)}. {sufixo_score}"

    meses_em_alta = 0
    indice_inicio = len(ordenado) - 1
    while (
        indice_inicio > 0
        and ordenado[indice_inicio][1] > ordenado[indice_inicio - 1][1]
    ):
        meses_em_alta += 1
        indice_inicio -= 1

    evasao_anterior = float(ordenado[-2][1])
    if meses_em_alta >= 2:
        evasao_inicial = float(ordenado[indice_inicio][1])
        return (
            f"A evasão sobe há {meses_em_alta} meses, de "
            f"{_formatar_percentual(evasao_inicial)} para {_formatar_percentual(evasao_atual)}. "
            f"{sufixo_score}"
        )
    if evasao_atual > evasao_anterior:
        return (
            f"A evasão aumentou no último mês, de {_formatar_percentual(evasao_anterior)} "
            f"para {_formatar_percentual(evasao_atual)}. {sufixo_score}"
        )
    if evasao_atual < evasao_anterior:
        return (
            f"A evasão reduziu no último mês, de {_formatar_percentual(evasao_anterior)} "
            f"para {_formatar_percentual(evasao_atual)}. {sufixo_score}"
        )
    return (
        f"A evasão manteve-se em {_formatar_percentual(evasao_atual)} no último mês. "
        f"{sufixo_score}"
    )
