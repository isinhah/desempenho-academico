const badgeClassByClasse = { A: 'class-badge--a', B: 'class-badge--b', D: 'class-badge--d' }

export function ClassBadge({ classe }) {
  const label = String(classe || '-').toUpperCase()
  const colorClass = badgeClassByClasse[label] || 'class-badge--default'
  return <span className={`class-badge ${colorClass}`}>Classe {label}</span>
}
