from dataclasses import dataclass
from datetime import date
from html import escape

from sqlalchemy import and_, select
from sqlalchemy.orm import Session, aliased

from app.domain.calculo_score import calcular_score_por_evasao
from app.models import Curso, Escola, HistoricoIndicador


@dataclass(frozen=True)
class CursoRelatorio:
    nome: str
    escola: str
    score: float
    classe: str
    variacao_score: float | None


@dataclass(frozen=True)
class RelatorioMensal:
    mes_referencia: date
    cursos_que_subiram: list[CursoRelatorio]
    cursos_em_atencao: list[CursoRelatorio]


def mes_anterior(mes: date) -> date:
    return date(mes.year - 1, 12, 1) if mes.month == 1 else date(mes.year, mes.month - 1, 1)


def gerar_relatorio_mensal(db: Session, mes_referencia: date) -> RelatorioMensal:
    """Monta o resumo a partir do mês solicitado e de seu mês anterior."""
    indicador_atual = aliased(HistoricoIndicador)
    indicador_anterior = aliased(HistoricoIndicador)
    registros = db.execute(
        select(
            Curso.nome,
            Escola.nome,
            indicador_atual.pct_evasao,
            indicador_anterior.pct_evasao,
        )
        .join(Escola, Curso.escola_id == Escola.id)
        .join(indicador_atual, indicador_atual.curso_id == Curso.id)
        .outerjoin(
            indicador_anterior,
            and_(
                indicador_anterior.curso_id == Curso.id,
                indicador_anterior.mes_referencia == mes_anterior(mes_referencia),
            ),
        )
        .where(indicador_atual.mes_referencia == mes_referencia)
    ).all()

    cursos_que_subiram: list[CursoRelatorio] = []
    cursos_em_atencao: list[CursoRelatorio] = []
    for nome, escola, evasao_atual, evasao_anterior in registros:
        resultado_atual = calcular_score_por_evasao(float(evasao_atual))
        variacao_score = (
            round(resultado_atual["score"] - calcular_score_por_evasao(float(evasao_anterior))["score"], 2)
            if evasao_anterior is not None
            else None
        )
        curso = CursoRelatorio(
            nome=nome,
            escola=escola,
            score=resultado_atual["score"],
            classe=resultado_atual["classe"],
            variacao_score=variacao_score,
        )
        if variacao_score is not None and variacao_score > 0:
            cursos_que_subiram.append(curso)
        if curso.classe in {"B", "D"}:
            cursos_em_atencao.append(curso)

    return RelatorioMensal(
        mes_referencia=mes_referencia,
        cursos_que_subiram=sorted(
            cursos_que_subiram,
            key=lambda curso: (-float(curso.variacao_score or 0), curso.nome.casefold()),
        )[:5],
        cursos_em_atencao=sorted(
            cursos_em_atencao,
            key=lambda curso: (curso.score, curso.nome.casefold()),
        )[:5],
    )


def _formatar_mes(mes: date) -> str:
    nomes = (
        "janeiro", "fevereiro", "março", "abril", "maio", "junho",
        "julho", "agosto", "setembro", "outubro", "novembro", "dezembro",
    )
    return f"{nomes[mes.month - 1]} de {mes.year}"


def _formatar_score(score: float) -> str:
    return f"{score:.2f}".replace(".", ",")


def _lista_html(cursos: list[CursoRelatorio], mostrar_variacao: bool) -> str:
    if not cursos:
        return "<p>Nenhum curso se enquadrou neste critério.</p>"

    itens = []
    for curso in cursos:
        complemento = (
            f" · +{_formatar_score(curso.variacao_score or 0)} pontos"
            if mostrar_variacao
            else f" · Classe {curso.classe}"
        )
        itens.append(
            f"<li><strong>{escape(curso.nome)}</strong> — {escape(curso.escola)}"
            f" · Score {_formatar_score(curso.score)}{complemento}</li>"
        )
    return f"<ul>{''.join(itens)}</ul>"


def _lista_texto(cursos: list[CursoRelatorio], mostrar_variacao: bool) -> str:
    if not cursos:
        return "Nenhum curso se enquadrou neste critério."
    return "\n".join(
        f"- {curso.nome} ({curso.escola}): score {_formatar_score(curso.score)}"
        + (
            f" · +{_formatar_score(curso.variacao_score or 0)} pontos"
            if mostrar_variacao
            else f" · Classe {curso.classe}"
        )
        for curso in cursos
    )


def montar_email(relatorio: RelatorioMensal) -> dict[str, str]:
    """Gera versões HTML e texto do e-mail a partir do relatório."""
    periodo = _formatar_mes(relatorio.mes_referencia)
    subiram_html = _lista_html(relatorio.cursos_que_subiram, mostrar_variacao=True)
    atencao_html = _lista_html(relatorio.cursos_em_atencao, mostrar_variacao=False)
    subiram_texto = _lista_texto(relatorio.cursos_que_subiram, mostrar_variacao=True)
    atencao_texto = _lista_texto(relatorio.cursos_em_atencao, mostrar_variacao=False)
    return {
        "assunto": f"Relatório mensal de desempenho — {periodo}",
        "html": (
            f"<h1>Relatório mensal de desempenho</h1><p>Referência: {periodo}.</p>"
            f"<h2>Cursos que mais subiram no ranking</h2>{subiram_html}"
            f"<h2>Cursos em atenção</h2>{atencao_html}"
        ),
        "texto": (
            f"Relatório mensal de desempenho — {periodo}\n\n"
            f"Cursos que mais subiram no ranking\n{subiram_texto}\n\n"
            f"Cursos em atenção\n{atencao_texto}"
        ),
    }
