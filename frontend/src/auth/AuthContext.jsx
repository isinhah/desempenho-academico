import { useEffect, useMemo, useState } from 'react'
import { obterUsuarioAtual } from '../services/cursosApi'
import { supabase, supabaseConfigurado } from '../services/supabase'
import { AuthContext } from './context'

export function AuthProvider({ children }) {
  const [session, setSession] = useState(null)
  const [carregando, setCarregando] = useState(supabaseConfigurado)
  const [perfil, setPerfil] = useState(null)
  const [erroPerfil, setErroPerfil] = useState('')

  useEffect(() => {
    if (!supabase) return undefined

    let ativo = true

    async function atualizarSessao(novaSessao) {
      if (!ativo) return
      setSession(novaSessao)
      setErroPerfil('')

      if (!novaSessao) {
        setPerfil(null)
        setCarregando(false)
        return
      }

      setCarregando(true)
      try {
        const novoPerfil = await obterUsuarioAtual()
        if (ativo) setPerfil(novoPerfil)
      } catch (error) {
        if (ativo) {
          setPerfil(null)
          setErroPerfil(error.message || 'Não foi possível carregar seu perfil de acesso.')
        }
      } finally {
        if (ativo) setCarregando(false)
      }
    }

    supabase.auth.getSession().then(({ data, error }) => {
      if (!error) void atualizarSessao(data.session)
      else if (ativo) setCarregando(false)
    })

    const { data: assinatura } = supabase.auth.onAuthStateChange((_evento, novaSessao) => {
      void atualizarSessao(novaSessao)
    })

    return () => {
      ativo = false
      assinatura.subscription.unsubscribe()
    }
  }, [])

  const valor = useMemo(() => ({
    session,
    usuario: session?.user ?? null,
    perfil,
    erroPerfil,
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
  }), [carregando, erroPerfil, perfil, session])

  return <AuthContext.Provider value={valor}>{children}</AuthContext.Provider>
}
