import { requisicaoAutenticada } from './api'

async function respostaJson(response, mensagemPadrao) {
  const corpo = await response.json().catch(() => null)
  if (!response.ok) throw new Error(corpo?.mensagem || mensagemPadrao)
  return corpo
}

export async function listarImportacoes() {
  const response = await requisicaoAutenticada('/administracao/importacoes')
  return respostaJson(response, 'Não foi possível carregar as importações.')
}

export async function enviarImportacao(arquivo) {
  const response = await requisicaoAutenticada('/administracao/importacoes/upload', {
    method: 'POST',
    body: arquivo,
    headers: {
      'Content-Type': 'text/csv',
      'X-File-Name': arquivo.name,
    },
  })
  return respostaJson(response, 'Não foi possível processar o arquivo.')
}
