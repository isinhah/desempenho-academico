import { useEffect, useMemo, useState } from 'react'
import { supabase, supabaseConfigurado } from '../services/supabase'
import { AuthContext } from './context'

export function AuthProvider({ children }) {
  const [session, setSession] = useState(null)
  const [carregando, setCarregando] = useState(supabaseConfigurado)

  useEffect(() => {
    if (!supabase) return undefined

    let ativo = true

    supabase.auth.getSession().then(({ data, error }) => {
      if (ativo && !error) setSession(data.session)
      if (ativo) setCarregando(false)
    })

    const { data: assinatura } = supabase.auth.onAuthStateChange((_evento, novaSessao) => {
      setSession(novaSessao)
      setCarregando(false)
    })

    return () => {
      ativo = false
      assinatura.subscription.unsubscribe()
    }
  }, [])

  const valor = useMemo(() => ({
    session,
    usuario: session?.user ?? null,
    carregando,
    configurado: supabaseConfigurado,
    async entrar(email, senha) {
      if (!supabase) throw new Error('A autenticação ainda não foi configurada.')
      const { error } = await supabase.auth.signInWithPassword({ email, password: senha })
      if (error) throw error
    },
    async sair() {
      if (!supabase) return
      const { error } = await supabase.auth.signOut()
      if (error) throw error
    },
  }), [carregando, session])

  return <AuthContext.Provider value={valor}>{children}</AuthContext.Provider>
}
