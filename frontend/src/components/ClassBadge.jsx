const badgeClassByClasse = {
  A: 'bg-emerald-100 text-emerald-800',
  B: 'bg-amber-100 text-amber-800',
}

export function ClassBadge({ classe }) {
  const label = String(classe || '-').toUpperCase()
  const colorClass = badgeClassByClasse[label] || 'bg-slate-200 text-slate-600'
  return <span className={`inline-flex min-w-8 items-center justify-center rounded-full px-2.5 py-1 text-xs font-extrabold ${colorClass}`}>Classe {label}</span>
}
