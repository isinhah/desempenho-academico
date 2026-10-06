import { ClassBadge } from './ClassBadge'
import { useRankingCursos } from '../hooks/useRankingCursos'

function formatarScore(score) {
  return Number(score).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

export function RankingCursos() {
  const { cursos, loading, error, recarregar } = useRankingCursos()
  return (
    <section className="ranking-card" aria-labelledby="ranking-title">
      <div className="ranking-card__header">
        <div>
          <h2 id="ranking-title">Cursos classificados</h2>
          {!loading && !error && <p>{cursos.length} curso(s) encontrado(s)</p>}
        </div>
      </div>
      {loading && <div className="ranking-feedback" role="status"><div className="ranking-feedback__content"><div className="spinner" aria-hidden="true" /><p>Carregando ranking de cursos...</p></div></div>}
      {error && !loading && <div className="ranking-feedback ranking-feedback--error" role="alert"><div className="ranking-feedback__content"><p>{error}</p><button className="retry-button" type="button" onClick={recarregar}>Tentar novamente</button></div></div>}
      {!loading && !error && (
        <div className="ranking-table-wrapper">
          <table className="ranking-table">
            <thead><tr><th scope="col">#</th><th scope="col">Nome do curso</th><th scope="col">Escola</th><th scope="col">Score</th><th scope="col">Selo</th></tr></thead>
            <tbody>
              {cursos.map((curso, index) => <tr key={curso.id}><td className="position">{index + 1}</td><td className="course-name">{curso.nome}</td><td className="school-name">{curso.escola}</td><td className="score">{formatarScore(curso.score)}</td><td><ClassBadge classe={curso.classe} /></td></tr>)}
              {cursos.length === 0 && <tr><td colSpan="5">Nenhum curso foi encontrado.</td></tr>}
            </tbody>
          </table>
        </div>
      )}
    </section>
  )
}
