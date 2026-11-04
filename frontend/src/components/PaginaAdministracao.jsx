import { useCallback, useEffect, useState } from 'react'
import { Navigate } from 'react-router-dom'
import { useAuth } from '../auth/useAuth'
import { Button } from '../ui'
import { enviarImportacao, listarImportacoes } from '../services/importacoesApi'

function formatarData(data) {
  return data ? new Date(data).toLocaleString('pt-BR', { dateStyle: 'short', timeStyle: 'short' }) : '—'
}

function formatarMes(data) {
  return new Date(`${data}T12:00:00`).toLocaleDateString('pt-BR', { month: 'short', year: 'numeric' })
}

const statusClasses = {
  CONCLUIDA: 'bg-emerald-50 text-emerald-800 ring-emerald-200',
  PROCESSANDO: 'bg-brand-50 text-brand-800 ring-brand-200',
  FALHA: 'bg-rose-50 text-rose-800 ring-rose-200',
  PENDENTE: 'bg-amber-50 text-amber-800 ring-amber-200',
}

export function PaginaAdministracao() {
  const { perfil } = useAuth()
  const [arquivo, setArquivo] = useState(null)
  const [importacoes, setImportacoes] = useState([])
  const [carregando, setCarregando] = useState(true)
  const [enviando, setEnviando] = useState(false)
  const [erro, setErro] = useState('')
  const [sucesso, setSucesso] = useState('')

  const carregarImportacoes = useCallback(async () => {
    setCarregando(true)
    try {
      setImportacoes(await listarImportacoes())
    } catch (error) {
      setErro(error.message || 'Não foi possível carregar as importações.')
    } finally {
      setCarregando(false)
    }
  }, [])

  useEffect(() => {
    if (perfil?.papel !== 'ADMINISTRADOR') return undefined

    let ativo = true
    listarImportacoes()
      .then((dados) => {
        if (ativo) setImportacoes(dados)
      })
      .catch((error) => {
        if (ativo) setErro(error.message || 'Não foi possível carregar as importações.')
      })
      .finally(() => {
        if (ativo) setCarregando(false)
      })

    return () => {
      ativo = false
    }
  }, [perfil?.papel])

  if (perfil?.papel !== 'ADMINISTRADOR') return <Navigate to="/" replace />

  async function processar(event) {
    event.preventDefault()
    const formulario = event.currentTarget
    if (!arquivo) {
      setErro('Selecione um arquivo CSV para continuar.')
      return
    }

    setEnviando(true)
    setErro('')
    setSucesso('')
    try {
      const resultado = await enviarImportacao(arquivo)
      setSucesso(`${resultado.nome_arquivo || arquivo.name} foi processado com ${resultado.registros_sincronizados} cursos.`)
      setArquivo(null)
      formulario.reset()
      await carregarImportacoes()
    } catch (error) {
      setErro(error.message || 'Não foi possível processar o arquivo.')
    } finally {
      setEnviando(false)
    }
  }

  return <main className="mx-auto w-[calc(100%-2rem)] max-w-6xl py-10 pb-16 max-sm:w-[calc(100%-1.5rem)]">
    <header className="mb-6">
      <p className="text-xs font-bold tracking-wide text-brand-700">ADMINISTRAÇÃO</p>
      <h1 className="mt-1 text-3xl font-bold tracking-tight text-slate-950">Importações mensais</h1>
      <p className="mt-1 text-sm text-slate-600">Envie e processe os indicadores mensais dos cursos.</p>
    </header>

    <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm" aria-labelledby="enviar-arquivo">
      <h2 id="enviar-arquivo" className="text-lg font-bold text-slate-900">Processar arquivo CSV</h2>
      <p className="mt-1 text-sm leading-6 text-slate-600">Use o formato <strong>cursos_YYYY-MM.csv</strong> com os 72 cursos.</p>
      <form className="mt-5 flex flex-col gap-4 sm:flex-row sm:items-end" onSubmit={processar}>
        <label className="grid flex-1 gap-1 text-sm font-semibold text-slate-700">Arquivo CSV<input type="file" accept=".csv,text/csv" onChange={(event) => setArquivo(event.target.files?.[0] || null)} disabled={enviando} className="block h-11 w-full cursor-pointer rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm font-normal text-slate-700 file:mr-3 file:border-0 file:bg-transparent file:font-semibold file:text-brand-700" /></label>
        <Button variant="primary" type="submit" disabled={enviando}>{enviando ? 'Processando...' : 'Enviar e processar'}</Button>
      </form>
      {erro && <p className="mt-4 rounded-xl bg-rose-50 px-4 py-3 text-sm font-medium text-rose-800" role="alert">{erro}</p>}
      {sucesso && <p className="mt-4 rounded-xl bg-emerald-50 px-4 py-3 text-sm font-medium text-emerald-800" role="status">{sucesso}</p>}
    </section>

    <section className="mt-6 overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm" aria-labelledby="importacoes-recentes">
      <div className="flex items-center justify-between gap-4 border-b border-slate-200 px-6 py-5"><div><h2 id="importacoes-recentes" className="text-lg font-bold text-slate-900">Importações recentes</h2><p className="mt-1 text-sm text-slate-600">Últimos arquivos enviados ao Storage.</p></div><Button onClick={() => void carregarImportacoes()} disabled={carregando || enviando}>Atualizar</Button></div>
      {carregando ? <div className="grid min-h-48 place-items-center text-sm text-slate-500" role="status"><span className="size-7 animate-spin rounded-full border-[3px] border-brand-100 border-t-brand-700" aria-hidden="true" /></div> : <div className="overflow-x-auto"><table className="w-full min-w-190 text-left"><thead className="bg-slate-50"><tr><th className="px-6 py-3 text-xs font-semibold text-slate-600">Arquivo</th><th className="px-5 py-3 text-xs font-semibold text-slate-600">Referência</th><th className="px-5 py-3 text-xs font-semibold text-slate-600">Linhas</th><th className="px-5 py-3 text-xs font-semibold text-slate-600">Status</th><th className="px-6 py-3 text-xs font-semibold text-slate-600">Processado em</th></tr></thead><tbody>{importacoes.map((item) => <tr key={item.id} className="border-t border-slate-100"><td className="px-6 py-4 font-semibold text-slate-900">{item.nome_arquivo}{item.mensagem_erro && <p className="mt-1 max-w-sm text-xs font-normal text-rose-700">{item.mensagem_erro}</p>}</td><td className="px-5 py-4 text-sm text-slate-600">{formatarMes(item.mes_referencia)}</td><td className="px-5 py-4 text-sm text-slate-600">{item.linhas_importadas}/{item.linhas_lidas}</td><td className="px-5 py-4"><span className={`inline-flex rounded-full px-3 py-1 text-xs font-semibold ring-1 ${statusClasses[item.status] || 'bg-slate-100 text-slate-700 ring-slate-200'}`}>{item.status}</span></td><td className="px-6 py-4 text-sm text-slate-600">{formatarData(item.processado_em)}</td></tr>)}{importacoes.length === 0 && <tr><td colSpan="5" className="px-6 py-10 text-center text-sm text-slate-500">Nenhuma importação processada ainda.</td></tr>}</tbody></table></div>}
    </section>
  </main>
}
