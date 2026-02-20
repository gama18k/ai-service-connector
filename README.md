# WatsonX RAG Webhook 🤖

Este repositório contém uma função Python adaptada para a **Vercel** que serve como ponte (webhook) entre o **Watson Assistant** e um deploy de **AI Service (RAG)** no WatsonX.

## Funcionalidades
* Autenticação automática com IBM Cloud IAM.
* Gestão de contexto (histórico da conversa).
* Chamada ao endpoint de RAG no WatsonX.
* Formatação de resposta compatível com Actions do Watson Assistant.

## Configuração
1. Clone o repositório.
2. Adicione suas credenciais no `api/index.py`.
3. Faça o deploy na Vercel.
4. Configure a URL gerada no painel de Webhooks do Watson Assistant.
