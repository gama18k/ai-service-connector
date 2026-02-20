from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route('/', methods=['POST'])
@app.route('/api/index', methods=['POST'])
def handler():
    # 1. Configurações Iniciais
    api_key = "htVumjBHrdw_0JMZ1TJCZnn0ZKf2ew9OP4QBAGNr32R9"
    url_watsonx = "https://au-syd.ml.cloud.ibm.com/ml/v4/deployments/962b8cc9-8697-46de-8452-ea01935d77d5/ai_service?version=2021-05-01"
    
    # Recebe os dados do Watson Assistant
    data = request.json or {}
    user_message = data.get("input", "")
    context = data.get("context", [])

    if not user_message:
        return jsonify({"error": "Nenhuma mensagem enviada."}), 400

    try:
        # --- 1. Autenticação com o IAM ---
        iam_url = "https://iam.cloud.ibm.com/identity/token"
        headers_iam = {"Content-Type": "application/x-www-form-urlencoded"}
        data_iam = {
            "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
            "apikey": api_key
        }
        
        token_res = requests.post(iam_url, headers=headers_iam, data=data_iam)
        token_res.raise_for_status()
        access_token = token_res.json().get("access_token")

        # --- 2. Atualiza Contexto com Mensagem do Usuário ---
        context.append({"role": "user", "content": user_message})

        # --- 3. Chamada ao WatsonX (RAG) ---
        headers_rag = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        payload_rag = {
            "input_data": [
                {
                    "values": [[user_message, context]]
                }
            ]
        }

        response = requests.post(url_watsonx, headers=headers_rag, json=payload_rag)
        response.raise_for_status()
        
        result = response.json()
        # O parsing abaixo assume que seu deploy retorna o texto na primeira posição
        assistant_reply = result['predictions'][0]['values'][0][0]

        # --- 4. Atualiza Contexto com Resposta do Assistente ---
        context.append({"role": "assistant", "content": assistant_reply})

        # --- 5. Retorno Final ---
        return jsonify({
            "response": assistant_reply,
            "context": context
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Necessário para execução local e Vercel
if __name__ == "__main__":
    app.run()
