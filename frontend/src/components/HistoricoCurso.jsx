import { ClassBadge, StatCard } from '../ui'
import { EvasionChart } from './EvasionChart'
import { useHistoricoCurso } from '../hooks/useHistoricoCurso'
import { formatarPercentual } from '../utils/formatters'

function formatarMes(data) {
  return new Intl.DateTimeFormat('pt-BR', { month: 'short', year: '2-digit' })
    .format(new Date(`${data}T12:00:00`))
    .replace('.', '')
}

function formatarPontosPercentuais(valor) {
  return `${valor > 0 ? '+' : ''}${Number(valor).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} p.p.`
}

export function HistoricoCurso({ curso, posicao, totalCursos }) {
  const { historico, loading, error } = useHistoricoCurso(curso.id)
  const atual = historico.at(-1)
  const anterior = historico.at(-2)
  const variacao = atual && anterior ? Number(atual.pct_evasao) - Number(anterior.pct_evasao) : null
  const dadosGrafico = historico.map((indicador) => ({ mes: formatarMes(indicador.mes_referencia), evasao: Number(indicador.pct_evasao) }))
  const tomVariacao = variacao === null || variacao === 0 ? 'neutral' : variacao > 0 ? 'bad' : 'good'
  const valorVariacao = variacao === null ? '—' : `${variacao > 0 ? '▲ ' : variacao < 0 ? '▼ ' : ''}${formatarPontosPercentuais(variacao)}`
  const textoVariacao = variacao === null ? 'São necessários dois meses' : variacao > 0 ? 'Aumentou desde o mês anterior' : variacao < 0 ? 'Reduziu desde o mês anterior' : 'Sem variação no último mês'

  return <section className="mt-4 overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm" aria-labelledby="history-title">
    <header className="flex flex-col gap-3 border-b border-slate-100 px-5 py-4 sm:flex-row sm:items-start sm:justify-between"><div><h2 id="history-title" className="text-xl font-bold tracking-tight text-slate-900">{curso.nome}</h2><p className="mt-0.5 text-sm text-slate-600">{curso.escola}{posicao && totalCursos ? ` · ${posicao}º de ${totalCursos} no ranking` : ''}</p></div><ClassBadge classe={curso.classe} /></header>
    <div className="grid grid-cols-1 gap-3 p-4 sm:grid-cols-2 xl:grid-cols-4"><StatCard label="Score atual" value={Number(curso.score).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} caption="em uma escala de 0 a 100" tone="brand" /><StatCard label="Alunos ativos" value={Number(curso.alunos_ativos).toLocaleString('pt-BR')} caption="no período mais recente" /><StatCard label="Alunos evadidos" value={Number(curso.alunos_evadidos).toLocaleString('pt-BR')} caption="no período mais recente" tone="warn" /><StatCard label="Evasão mais recente" value={atual ? formatarPercentual(atual.pct_evasao) : '—'} caption={atual ? formatarMes(atual.mes_referencia) : 'Sem histórico'} tone="bad" /></div>
    <div className="px-4 pb-4"><StatCard label="Variação da evasão" value={valorVariacao} caption={textoVariacao} tone={tomVariacao} /></div>
    {curso.resumo_academico && <div className="px-4 pb-4"><section className="rounded-xl border border-brand-100 bg-brand-50 px-4 py-3" aria-labelledby="resumo-automatico"><h3 id="resumo-automatico" className="text-sm font-bold text-brand-900">Resumo automático</h3><p className="mt-1 text-sm leading-6 text-brand-900">{curso.resumo_academico}</p>{curso.resumo_referencia && <p className="mt-2 text-xs text-brand-700">Atualizado com os dados de {formatarMes(curso.resumo_referencia)}.</p>}</section></div>}
    {loading && <div className="grid min-h-57.5 place-items-center p-6 text-center text-slate-500" role="status">Carregando histórico...</div>}
    {error && !loading && <div className="grid min-h-57.5 place-items-center p-6 text-center text-rose-700" role="alert">{error}</div>}
    {!loading && !error && dadosGrafico.length === 0 && <div className="grid min-h-57.5 place-items-center p-6 text-center text-slate-500">Não há indicadores para este curso.</div>}
    {!loading && !error && dadosGrafico.length > 0 && <div className="border-t border-slate-100 px-4 pb-4 pt-5"><div className="flex items-baseline justify-between pb-2"><h3 className="text-sm font-bold text-slate-900">Evolução da evasão</h3><span className="text-xs text-slate-600">Percentual por mês</span></div><EvasionChart data={dadosGrafico} /></div>}
  </section>
}
