# Changelog

Todas as mudancas relevantes deste projeto serao documentadas neste arquivo.

O formato segue a ideia do Keep a Changelog, adaptado para o contexto do projeto.

## [1.0.0] - 2026-03-07

### Adicionado
- Estrutura inicial da API em Flask
- Rotas `GET /` e `POST /`
- Suporte a `/api/index` para deploy serverless
- Integracao com autenticacao IAM da IBM Cloud
- Encaminhamento de prompts para IBM watsonx
- Configuracao de deploy com Vercel
- Suporte a variaveis de ambiente com `.env`
- Documentacao inicial do projeto

### Melhorado
- README reescrito para publicacao no GitHub
- Instrucoes de execucao local mais claras
- Documentacao de endpoints, payload e fluxo da aplicacao
- Exemplos de uso com `curl`
- Orientacoes de deploy na Vercel

### Observacoes
- Esta versao envia uma mensagem por requisicao no campo `messages`
- A resposta da API e retornada no formato `{ "response": "..." }`
- O projeto ainda nao possui testes automatizados
