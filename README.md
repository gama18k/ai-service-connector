# AI Service Connector for IBM watsonx

API em Python/Flask para receber mensagens via webhook, autenticar na IBM Cloud com IAM e encaminhar prompts para um endpoint do IBM watsonx. O projeto foi estruturado para deploy serverless na Vercel.

## O que este projeto faz

- Recebe requisições `POST` em `/` ou `/api/index`
- Aceita texto em campos como `input`, `text`, `message` ou `parameters.input`
- Gera token IAM usando `WATSONX_API_KEY`
- Encaminha a mensagem para a URL definida em `WATSONX_URL`
- Normaliza a resposta em JSON no formato `{ "response": "..." }`

## Stack

- Python 3
- Flask
- Requests
- python-dotenv
- Vercel
- IBM watsonx / IBM Cloud IAM

## Estrutura

```text
.
├── api/
│   └── index.py
├── .gitignore
├── README.md
├── requirements.txt
└── vercel.json
```

## Variaveis de ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
WATSONX_API_KEY=sua_chave_api_ibm_cloud
WATSONX_URL=https://...
```

Descricao:

- `WATSONX_API_KEY`: API key usada para gerar o token IAM
- `WATSONX_URL`: endpoint HTTP do deployment/modelo no watsonx

## Executando localmente

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 api/index.py
```

Servidor local padrao:

```text
http://localhost:5000
```

Teste rapido:

```bash
curl -X POST http://localhost:5000/ \
  -H "Content-Type: application/json" \
  -d '{"input":"Oi, WatsonX"}'
```

Resposta esperada:

```json
{
  "response": "..."
}
```

## Endpoints

### `GET /`

Health check simples.

Resposta:

```text
Webhook RAG esta Online!
```

### `POST /`

Recebe o payload do cliente e envia a mensagem ao watsonx.

Campos aceitos para extrair o texto:

- `input`
- `text`
- `message`
- `parameters.input`
- `parameters.text`

Exemplo de payload:

```json
{
  "input": "Explique o que e RAG em uma frase."
}
```

## Fluxo da aplicacao

1. O cliente envia uma mensagem para o webhook.
2. A API extrai o texto do JSON recebido.
3. O conector solicita um token IAM na IBM Cloud.
4. A mensagem e enviada para o endpoint configurado em `WATSONX_URL`.
5. A resposta da IBM e retornada ao cliente em `{ "response": "..." }`.

## Deploy na Vercel

O arquivo [`vercel.json`](/Users/eduardagama/Downloads/projects%202/RAG-AI-CONNECTOR/vercel.json) reescreve qualquer rota para `/api/index`, permitindo expor a API pela raiz do dominio.

Passos:

```bash
npm i -g vercel
vercel
```

Depois, configure no painel da Vercel:

- `WATSONX_API_KEY`
- `WATSONX_URL`

## Publicando no GitHub

O repositorio local ja possui um remoto `origin`. Para publicar as alteracoes atuais:

```bash
git add .
git commit -m "docs: improve README for GitHub publication"
git push origin main
```

Se quiser criar um repositorio novo em vez de usar o remoto atual:

```bash
git remote remove origin
git remote add origin https://github.com/SEU_USUARIO/SEU_REPOSITORIO.git
git branch -M main
git push -u origin main
```

## Observacoes

- O projeto hoje envia apenas uma mensagem por requisicao no campo `messages`
- Em caso de falha, a API responde com um texto de erro dentro de `response`
- Nao ha suite de testes automatizados no repositorio neste momento
