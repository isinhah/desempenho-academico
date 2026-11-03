from collections import Counter
from dataclasses import dataclass
from datetime import date
from html import escape

from sqlalchemy import and_, select
from sqlalchemy.orm import Session, aliased

from app.domain.calculo_score import calcular_score_por_evasao
from app.models import Curso, Escola, HistoricoIndicador


@dataclass(frozen=True)
class CursoRelatorio:
    id: int
    nome: str
    escola: str
    score: float
    classe: str
    pct_evasao: float
    variacao_score: float | None
    variacao_evasao: float | None


@dataclass(frozen=True)
class RelatorioDecano:
    mes_referencia: date
    total_cursos: int
    score_medio: float | None
    quantidade_por_classe: dict[str, int]
    cursos_que_subiram: list[CursoRelatorio]
    cursos_em_atencao: list[CursoRelatorio]


@dataclass(frozen=True)
class ResumoCoordenador:
    mes_referencia: date
    cursos: list[CursoRelatorio]


def mes_anterior(mes: date) -> date:
    return date(mes.year - 1, 12, 1) if mes.month == 1 else date(mes.year, mes.month - 1, 1)


def _consultar_cursos(
    db: Session, mes_referencia: date, cursos_ids: tuple[int, ...] | None = None
) -> list[CursoRelatorio]:
    if cursos_ids is not None and not cursos_ids:
        return []

    indicador_atual = aliased(HistoricoIndicador)
    indicador_anterior = aliased(HistoricoIndicador)
    consulta = (
        select(
            Curso.id,
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
    )
    if cursos_ids is not None:
        consulta = consulta.where(Curso.id.in_(cursos_ids))

    cursos: list[CursoRelatorio] = []
    for curso_id, nome, escola, evasao_atual, evasao_anterior in db.execute(consulta).all():
        resultado_atual = calcular_score_por_evasao(float(evasao_atual))
        resultado_anterior = (
            calcular_score_por_evasao(float(evasao_anterior))
            if evasao_anterior is not None
            else None
        )
        cursos.append(
            CursoRelatorio(
                id=curso_id,
                nome=nome,
                escola=escola,
                score=resultado_atual["score"],
                classe=resultado_atual["classe"],
                pct_evasao=float(evasao_atual),
                variacao_score=(
                    round(resultado_atual["score"] - resultado_anterior["score"], 2)
                    if resultado_anterior is not None
                    else None
                ),
                variacao_evasao=(
                    round(float(evasao_atual) - float(evasao_anterior), 2)
                    if evasao_anterior is not None
                    else None
                ),
            )
        )
    return cursos


def gerar_relatorio_decano(db: Session, mes_referencia: date) -> RelatorioDecano:
    cursos = _consultar_cursos(db, mes_referencia)
    cursos_que_subiram = sorted(
        (curso for curso in cursos if (curso.variacao_score or 0) > 0),
        key=lambda curso: (-float(curso.variacao_score or 0), curso.nome.casefold()),
    )[:5]
    cursos_em_atencao = sorted(
        (curso for curso in cursos if curso.classe in {"B", "D"}),
        key=lambda curso: (curso.score, curso.nome.casefold()),
    )[:5]
    return RelatorioDecano(
        mes_referencia=mes_referencia,
        total_cursos=len(cursos),
        score_medio=round(sum(curso.score for curso in cursos) / len(cursos), 2) if cursos else None,
        quantidade_por_classe=dict(Counter(curso.classe for curso in cursos)),
        cursos_que_subiram=cursos_que_subiram,
        cursos_em_atencao=cursos_em_atencao,
    )


def gerar_resumo_coordenador(
    db: Session, mes_referencia: date, cursos_ids: tuple[int, ...]
) -> ResumoCoordenador:
    return ResumoCoordenador(
        mes_referencia=mes_referencia,
        cursos=sorted(
            _consultar_cursos(db, mes_referencia, cursos_ids),
            key=lambda curso: curso.nome.casefold(),
        ),
    )


def _formatar_mes(mes: date) -> str:
    nomes = (
        "janeiro", "fevereiro", "março", "abril", "maio", "junho",
        "julho", "agosto", "setembro", "outubro", "novembro", "dezembro",
    )
    return f"{nomes[mes.month - 1]} de {mes.year}"


def _formatar_score(score: float) -> str:
    return f"{score:.2f}".replace(".", ",")


def _formatar_percentual(valor: float) -> str:
    return f"{valor:.2f}%".replace(".", ",")


def _lista_html(cursos: list[CursoRelatorio], tipo: str) -> str:
    if not cursos:
        return "<p>Nenhum curso se enquadrou neste critério.</p>"
    itens = []
    for curso in cursos:
        complemento = (
            f" · +{_formatar_score(curso.variacao_score or 0)} pontos"
            if tipo == "melhoria"
            else f" · Classe {curso.classe} · Evasão {_formatar_percentual(curso.pct_evasao)}"
        )
        itens.append(
            f"<li><strong>{escape(curso.nome)}</strong> — {escape(curso.escola)}"
            f" · Score {_formatar_score(curso.score)}{complemento}</li>"
        )
    return f"<ul>{''.join(itens)}</ul>"


def _lista_texto(cursos: list[CursoRelatorio], tipo: str) -> str:
    if not cursos:
        return "Nenhum curso se enquadrou neste critério."
    return "\n".join(
        f"- {curso.nome} ({curso.escola}): score {_formatar_score(curso.score)}"
        + (
            f" · +{_formatar_score(curso.variacao_score or 0)} pontos"
            if tipo == "melhoria"
            else f" · Classe {curso.classe} · Evasão {_formatar_percentual(curso.pct_evasao)}"
        )
        for curso in cursos
    )


def montar_email_decano(nome: str, relatorio: RelatorioDecano) -> dict[str, str]:
    periodo = _formatar_mes(relatorio.mes_referencia)
    distribuicao = " · ".join(
        f"Classe {classe}: {relatorio.quantidade_por_classe.get(classe, 0)}"
        for classe in ("A", "B", "D")
    )
    score_medio = _formatar_score(relatorio.score_medio) if relatorio.score_medio is not None else "—"
    return {
        "assunto": f"Resumo mensal acadêmico institucional — {periodo}",
        "html": (
            f"<h1>Resumo mensal acadêmico institucional</h1><p>Olá, {escape(nome)}.</p>"
            f"<p>Referência: {periodo}.</p><h2>Resumo</h2><ul>"
            f"<li>Cursos analisados: {relatorio.total_cursos}</li>"
            f"<li>Score médio: {score_medio}</li><li>{distribuicao}</li></ul>"
            f"<h2>Destaques positivos</h2>{_lista_html(relatorio.cursos_que_subiram, 'melhoria')}"
            f"<h2>Cursos em atenção</h2>{_lista_html(relatorio.cursos_em_atencao, 'atencao')}"
            "<p>Acesse o dashboard para comparar cursos e escolas.</p>"
        ),
        "texto": (
            f"Resumo mensal acadêmico institucional — {periodo}\n\nOlá, {nome}.\n\n"
            f"Cursos analisados: {relatorio.total_cursos}\nScore médio: {score_medio}\n{distribuicao}\n\n"
            f"Destaques positivos\n{_lista_texto(relatorio.cursos_que_subiram, 'melhoria')}\n\n"
            f"Cursos em atenção\n{_lista_texto(relatorio.cursos_em_atencao, 'atencao')}\n\n"
            "Acesse o dashboard para comparar cursos e escolas."
        ),
    }


def _secao_coordenador_html(curso: CursoRelatorio) -> str:
    variacao_score = (
        f"{curso.variacao_score:+.2f}".replace(".", ",") + " ponto(s)"
        if curso.variacao_score is not None else "sem comparação disponível"
    )
    variacao_evasao = (
        f"{curso.variacao_evasao:+.2f}".replace(".", ",") + " p.p."
        if curso.variacao_evasao is not None else "sem comparação disponível"
    )
    alerta = "A evasão aumentou em relação ao mês anterior." if (curso.variacao_evasao or 0) > 0 else "Acompanhe a evolução da evasão no dashboard."
    return (
        f"<h2>{escape(curso.nome)}</h2><p>{escape(curso.escola)}</p><ul>"
        f"<li>Score: {_formatar_score(curso.score)} · Classe {curso.classe}</li>"
        f"<li>Evasão: {_formatar_percentual(curso.pct_evasao)}</li>"
        f"<li>Variação do score: {variacao_score}</li>"
        f"<li>Variação da evasão: {variacao_evasao}</li></ul>"
        f"<p><strong>Ponto de atenção:</strong> {alerta}</p>"
    )


def _secao_coordenador_texto(curso: CursoRelatorio) -> str:
    variacao_score = f"{curso.variacao_score:+.2f}".replace(".", ",") + " ponto(s)" if curso.variacao_score is not None else "sem comparação disponível"
    variacao_evasao = f"{curso.variacao_evasao:+.2f}".replace(".", ",") + " p.p." if curso.variacao_evasao is not None else "sem comparação disponível"
    alerta = "A evasão aumentou em relação ao mês anterior." if (curso.variacao_evasao or 0) > 0 else "Acompanhe a evolução da evasão no dashboard."
    return (
        f"{curso.nome} — {curso.escola}\nScore: {_formatar_score(curso.score)} · Classe {curso.classe}\n"
        f"Evasão: {_formatar_percentual(curso.pct_evasao)}\nVariação do score: {variacao_score}\n"
        f"Variação da evasão: {variacao_evasao}\nPonto de atenção: {alerta}"
    )


def montar_email_coordenador(nome: str, resumo: ResumoCoordenador) -> dict[str, str]:
    periodo = _formatar_mes(resumo.mes_referencia)
    secoes_html = "".join(_secao_coordenador_html(curso) for curso in resumo.cursos)
    secoes_texto = "\n\n".join(_secao_coordenador_texto(curso) for curso in resumo.cursos)
    if not resumo.cursos:
        secoes_html = "<p>Não há indicadores consolidados para os seus cursos neste período.</p>"
        secoes_texto = "Não há indicadores consolidados para os seus cursos neste período."
    return {
        "assunto": f"Resumo mensal acadêmico dos seus cursos — {periodo}",
        "html": (
            f"<h1>Resumo mensal acadêmico dos seus cursos</h1><p>Olá, {escape(nome)}.</p>"
            f"<p>Referência: {periodo}.</p>{secoes_html}"
            "<p>Acesse o dashboard para acompanhar o histórico completo.</p>"
        ),
        "texto": (
            f"Resumo mensal acadêmico dos seus cursos — {periodo}\n\nOlá, {nome}.\n\n{secoes_texto}\n\n"
            "Acesse o dashboard para acompanhar o histórico completo."
        ),
    }
