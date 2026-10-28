const classes = {
  A: { badge: 'bg-emerald-50 text-emerald-800 ring-1 ring-emerald-200', dot: 'bg-emerald-500', bar: 'bg-emerald-500' },
  B: { badge: 'bg-amber-50 text-amber-800 ring-1 ring-amber-200', dot: 'bg-amber-500', bar: 'bg-amber-500' },
}

export function Button({ variant = 'secondary', className = '', ...props }) {
  const variants = {
    primary: 'bg-brand-700 text-white shadow-sm hover:bg-brand-800 active:bg-brand-900',
    secondary: 'border border-slate-300 bg-white text-slate-700 hover:border-slate-400 hover:bg-slate-50',
  }

  return <button type="button" {...props} className={`inline-flex min-h-10 items-center justify-center gap-2 rounded-lg px-4 text-sm font-semibold transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-brand-600 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 ${variants[variant]} ${className}`} />
}

export function ClassBadge({ classe }) {
  const label = String(classe || '-').toUpperCase()
  const classeVisual = classes[label] || { badge: 'bg-slate-100 text-slate-700 ring-1 ring-slate-200', dot: 'bg-slate-400', bar: 'bg-slate-400' }

  return <span className={`inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-semibold ${classeVisual.badge}`}><span className={`size-1.5 rounded-full ${classeVisual.dot}`} aria-hidden="true" />Classe {label}</span>
}

export function RankBadge({ position }) {
  return <span className={`flex size-9 items-center justify-center rounded-full text-sm font-bold ${position <= 3 ? 'bg-brand-700 text-white' : 'bg-slate-100 text-slate-700'}`}>{position}</span>
}

export function ScoreBar({ score, classe }) {
  const classeVisual = classes[classe] || classes.B
  return <div className="min-w-32"><div className="text-base font-semibold tabular-nums text-slate-900">{Number(score).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</div><div className="mt-1.5 h-1.5 overflow-hidden rounded-full bg-slate-200" aria-hidden="true"><div className={`h-full rounded-full ${classeVisual.bar}`} style={{ width: `${Math.max(0, Math.min(100, Number(score)))}%` }} /></div></div>
}

const tones = {
  neutral: { dot: 'bg-slate-500', value: 'text-slate-900' },
  brand: { dot: 'bg-brand-600', value: 'text-slate-900' },
  good: { dot: 'bg-emerald-500', value: 'text-emerald-800' },
  warn: { dot: 'bg-amber-500', value: 'text-amber-800' },
  bad: { dot: 'bg-rose-500', value: 'text-rose-700' },
}

export function StatCard({ label, value, caption, tone = 'neutral' }) {
  const estilo = tones[tone]
  return <article className="min-w-0 rounded-2xl border border-slate-200 bg-white px-5 py-4 shadow-sm"><div className="flex items-center gap-2 text-sm text-slate-600"><span className={`size-1.5 rounded-full ${estilo.dot}`} aria-hidden="true" />{label}</div><div className={`mt-1.5 truncate text-3xl font-bold tracking-tight ${estilo.value}`}>{value}</div>{caption && <div className="mt-1 text-sm text-slate-600">{caption}</div>}</article>
}

export function FilterTabs({ options, value, onChange }) {
  return <div role="tablist" className="inline-flex max-w-full gap-1 overflow-x-auto rounded-xl bg-slate-100 p-1">{options.map((option) => <button key={option.value} type="button" role="tab" aria-selected={value === option.value} onClick={() => onChange(option.value)} className={`min-h-9 shrink-0 rounded-lg px-3 text-sm font-semibold transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-brand-600 ${value === option.value ? 'bg-white text-brand-800 shadow-sm' : 'text-slate-600 hover:text-slate-900'}`}>{option.label} <span className="font-normal text-slate-500">{option.count}</span></button>)}</div>
}

export function Callout({ tone = 'good', children }) {
  const styles = tone === 'bad' ? 'bg-rose-50 text-rose-900' : 'bg-emerald-50 text-emerald-900'
  return <div className={`rounded-xl px-4 py-3 text-sm font-medium ${styles}`}>{children}</div>
}
