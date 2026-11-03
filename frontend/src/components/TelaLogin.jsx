import { useState } from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from '../auth/useAuth'

export function TelaLogin() {
  const { usuario, configurado, entrar } = useAuth()
  const location = useLocation()
  const [email, setEmail] = useState('')
  const [senha, setSenha] = useState('')
  const [enviando, setEnviando] = useState(false)
  const [erro, setErro] = useState('')

  if (usuario) return <Navigate to={location.state?.from?.pathname || '/'} replace />

  async function enviar(event) {
    event.preventDefault()
    setErro('')
    setEnviando(true)

    try {
      await entrar(email, senha)
    } catch {
      setErro('E-mail ou senha inválidos. Verifique os dados e tente novamente.')
    } finally {
      setEnviando(false)
    }
  }

  return (
    <main className="mx-auto flex min-h-[calc(100vh-4px)] w-[calc(100%-2rem)] max-w-md items-center py-10 max-sm:w-[calc(100%-1.5rem)]">
      <section className="w-full rounded-2xl border border-brand-100 bg-white p-7 shadow-sm sm:p-8" aria-labelledby="titulo-login">
        <p className="text-xs font-bold tracking-wide text-accent-700">PUCPR</p>
        <h1 id="titulo-login" className="mt-2 text-3xl font-bold tracking-tight text-ink">Acesse a análise de cursos</h1>
        <p className="mt-2 text-sm leading-6 text-slate-600">Entre com suas credenciais institucionais para consultar os indicadores disponíveis ao seu perfil.</p>

        {!configurado && (
          <div className="mt-6 rounded-xl bg-amber-50 px-4 py-3 text-sm text-amber-900" role="alert">
            Configure <code className="font-semibold">VITE_SUPABASE_URL</code> e <code className="font-semibold">VITE_SUPABASE_ANON_KEY</code> no arquivo <code className="font-semibold">frontend/.env</code> para habilitar o login.
          </div>
        )}

        <form className="mt-7 space-y-5" onSubmit={enviar}>
          <label className="block text-sm font-semibold text-slate-800">
            E-mail
            <input
              type="email"
              autoComplete="email"
              required
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              disabled={!configurado || enviando}
              className="mt-2 h-11 w-full rounded-lg border border-slate-300 bg-white px-3 text-slate-950 outline-none transition placeholder:text-slate-400 focus:border-brand-600 focus:ring-2 focus:ring-brand-600/25 disabled:cursor-not-allowed disabled:bg-slate-100"
              placeholder="nome@faculdade.br"
            />
          </label>
          <label className="block text-sm font-semibold text-slate-800">
            Senha
            <input
              type="password"
              autoComplete="current-password"
              required
              value={senha}
              onChange={(event) => setSenha(event.target.value)}
              disabled={!configurado || enviando}
              className="mt-2 h-11 w-full rounded-lg border border-slate-300 bg-white px-3 text-slate-950 outline-none transition placeholder:text-slate-400 focus:border-brand-600 focus:ring-2 focus:ring-brand-600/25 disabled:cursor-not-allowed disabled:bg-slate-100"
            />
          </label>

          {erro && <p className="rounded-xl bg-rose-50 px-4 py-3 text-sm font-medium text-rose-800" role="alert">{erro}</p>}

          <button
            type="submit"
            disabled={!configurado || enviando}
            className="inline-flex h-11 w-full items-center justify-center rounded-lg bg-brand-700 px-5 text-sm font-semibold text-white shadow-sm transition hover:bg-brand-800 focus:outline-none focus-visible:ring-2 focus-visible:ring-brand-600 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {enviando ? 'Entrando...' : 'Entrar'}
          </button>
        </form>
      </section>
    </main>
  )
}
