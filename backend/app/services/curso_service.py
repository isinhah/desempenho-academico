from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.domain.calculo_score import calcular_score_por_evasao
from app.dtos.curso_dto import (
    CursoDetalheResponse,
    HistoricoIndicadorResponse,
    CursoResponse,
)
from app.exceptions import ResourceNotFoundException
from app.models import Curso, Escola, HistoricoIndicador


class CursoService:
    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def _consulta_com_ultimo_indicador() -> Select:
        ultimo_indicador_id = (
            select(HistoricoIndicador.id)
            .where(HistoricoIndicador.curso_id == Curso.id)
            .order_by(
                HistoricoIndicador.mes_referencia.desc(), HistoricoIndicador.id.desc()
            )
            .limit(1)
            .correlate(Curso)
            .scalar_subquery()
        )
        return (
            select(Curso, Escola.nome, HistoricoIndicador)
            .join(Escola, Curso.escola_id == Escola.id)
            .outerjoin(HistoricoIndicador, HistoricoIndicador.id == ultimo_indicador_id)
        )

    @staticmethod
    def _montar_resposta(
        curso: Curso, escola: str, historico: HistoricoIndicador | None
    ) -> CursoDetalheResponse:
        pct_evasao = float(historico.pct_evasao) if historico else 0.0
        score = calcular_score_por_evasao(pct_evasao)
        return CursoDetalheResponse(
            id=curso.id,
            nome=curso.nome,
            escola=escola,
            alunos_ativos=curso.alunos_ativos,
            alunos_evadidos=curso.alunos_evadidos,
            pct_evasao=float(historico.pct_evasao) if historico else None,
            mes_referencia=historico.mes_referencia if historico else None,
            score=score["score"],
            classe=score["classe"],
        )

    def listar_cursos_com_score(
        self, escola_id: int | None = None
    ) -> list[CursoResponse]:
        consulta = self._consulta_com_ultimo_indicador()
        if escola_id is not None:
            consulta = consulta.where(Curso.escola_id == escola_id)

        registros = self.db.execute(consulta).all()
        cursos = [
            CursoResponse(**self._montar_resposta(*registro).model_dump())
            for registro in registros
        ]
        return sorted(cursos, key=lambda curso: (-curso.score, curso.nome.casefold()))

    def obter_curso(self, curso_id: int) -> CursoDetalheResponse:
        registro = self.db.execute(
            self._consulta_com_ultimo_indicador().where(Curso.id == curso_id)
        ).one_or_none()
        if registro is None:
            raise ResourceNotFoundException("Curso não encontrado.")
        return self._montar_resposta(*registro)

    def listar_historico(self, curso_id: int) -> list[HistoricoIndicadorResponse]:
        if self.db.get(Curso, curso_id) is None:
            raise ResourceNotFoundException("Curso não encontrado.")

        historicos = self.db.scalars(
            select(HistoricoIndicador)
            .where(HistoricoIndicador.curso_id == curso_id)
            .order_by(HistoricoIndicador.mes_referencia)
        ).all()
        return [
            HistoricoIndicadorResponse(
                mes_referencia=historico.mes_referencia,
                pct_evasao=float(historico.pct_evasao),
            )
            for historico in historicos
        ]
