"""Regras de negócio e persistência de cursos."""

from datetime import date

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.domain.calculo_score import calcular_score_com_peso_efetivo
from app.domain.auditoria import registrar_auditoria
from app.dtos.curso_dto import (
    CursoCreateRequest,
    CursoDetalheResponse,
    HistoricoIndicadorResponse,
    CursoResponse,
    CursoUpdateRequest,
)
from app.exceptions import (
    BusinessRuleException,
    ConflictException,
    ResourceNotFoundException,
)
from app.models import Curso, Escola, HistoricoIndicador


class CursoService:
    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def _calcular_pct_evasao(alunos_ativos: int, alunos_evadidos: int) -> float:
        if alunos_ativos == 0:
            return 0.0
        return round((alunos_evadidos / alunos_ativos) * 100, 2)

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
        dimensoes = {
            "financeiro": {
                "peso_dimensao": 0.65,
                "indicadores": [
                    {"nome": "pct_rb_rol", "valor": 85, "peso_indicador": 0.70},
                    {"nome": "pct_gp_rol", "valor": 75, "peso_indicador": 0.30},
                ],
            },
            "academico": {
                "peso_dimensao": 0.35,
                "indicadores": [
                    {
                        "nome": "pct_evasao_invertido",
                        "valor": 100 - pct_evasao,
                        "peso_indicador": 1.0,
                    }
                ],
            },
        }
        score = calcular_score_com_peso_efetivo(dimensoes)
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
        return [
            CursoResponse(**self._montar_resposta(*registro).model_dump())
            for registro in registros
        ]

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

    def criar_curso(self, dados: CursoCreateRequest) -> CursoDetalheResponse:
        escola = self.db.get(Escola, dados.escola_id)
        if escola is None:
            raise ResourceNotFoundException("Escola não encontrada.")

        existe = self.db.scalar(
            select(Curso.id).where(
                Curso.escola_id == dados.escola_id, Curso.nome == dados.nome
            )
        )
        if existe is not None:
            raise ConflictException("Já existe um curso com este nome nesta escola.")

        curso = Curso(**dados.model_dump())
        self.db.add(curso)
        self.db.flush()
        self._registrar_indicador(curso)
        self.db.commit()
        return self.obter_curso(curso.id)

    def atualizar_curso(
        self, curso_id: int, dados: CursoUpdateRequest
    ) -> CursoDetalheResponse:
        curso = self.db.get(Curso, curso_id)
        if curso is None:
            raise ResourceNotFoundException("Curso não encontrado.")

        score_anterior = self.obter_curso(curso_id).score

        alteracoes = dados.model_dump(exclude_unset=True)
        for campo, valor in alteracoes.items():
            setattr(curso, campo, valor)

        if curso.alunos_evadidos > curso.alunos_ativos:
            raise BusinessRuleException(
                "alunos_evadidos não pode ser maior que alunos_ativos."
            )
        if {"alunos_ativos", "alunos_evadidos"} & alteracoes.keys():
            self._registrar_indicador(curso)

        self.db.flush()
        resposta = self.obter_curso(curso_id)
        registrar_auditoria(
            self.db,
            curso_id=curso.id,
            valor_antigo=score_anterior,
            valor_novo=resposta.score,
        )
        self.db.commit()
        return resposta

    def excluir_curso(self, curso_id: int) -> None:
        curso = self.db.get(Curso, curso_id)
        if curso is None:
            raise ResourceNotFoundException("Curso não encontrado.")
        self.db.delete(curso)
        self.db.commit()

    def _registrar_indicador(self, curso: Curso) -> None:
        self.db.add(
            HistoricoIndicador(
                curso_id=curso.id,
                mes_referencia=date.today(),
                pct_evasao=self._calcular_pct_evasao(
                    curso.alunos_ativos, curso.alunos_evadidos
                ),
            )
        )
