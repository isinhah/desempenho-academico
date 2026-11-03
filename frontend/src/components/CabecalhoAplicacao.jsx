import { useAuth } from '../auth/useAuth'

const rotulosPapel = {
  DECANO: 'Decano',
  COORDENADOR_CURSO: 'Coordenador de curso',
}

export function CabecalhoAplicacao() {
  const { perfil, sair } = useAuth()
  const papel = rotulosPapel[perfil?.papel] || 'Usuário'

  return (
    <header className="border-b border-brand-100 bg-white">
      <div className="mx-auto flex w-[calc(100%-2rem)] max-w-6xl items-center justify-between gap-4 py-3 max-sm:w-[calc(100%-1.5rem)]">
        <div>
          <p className="text-xs font-bold tracking-wide text-brand-700">PUCPR</p>
        </div>
        <div className="flex items-center gap-3">
          <div className="hidden text-right sm:block">
            <p className="text-sm font-semibold text-slate-900">{perfil?.nome}</p>
            <p className="text-xs text-slate-600">{papel}</p>
          </div>
          <span className="inline-flex rounded-full bg-brand-50 px-3 py-1.5 text-xs font-semibold text-brand-800 sm:hidden">{papel}</span>
          <button
            type="button"
            onClick={() => sair()}
            className="inline-flex h-10 items-center justify-center rounded-lg border border-brand-200 bg-white px-3 text-sm font-semibold text-brand-800 transition hover:bg-brand-50 focus:outline-none focus-visible:ring-2 focus-visible:ring-brand-600 focus-visible:ring-offset-2"
          >
            Sair
          </button>
        </div>
      </div>
    </header>
  )
}
