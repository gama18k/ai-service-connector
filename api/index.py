from flask import Flask, request, jsonify
import requests
import json

app = Flask(__name__)

@app.route('/', methods=['POST', 'GET'])
@app.route('/api/index', methods=['POST', 'GET'])
def handler():
    # Para teste rápido no navegador
    if request.method == 'GET':
        return "Webhook RAG está Online!", 200

    # Configurações (Mantenha as suas)
    api_key = "htVumjBHrdw_0JMZ1TJCZnn0ZKf2ew9OP4QBAGNr32R9"
    url_watsonx = "https://au-syd.ml.cloud.ibm.com/ml/v4/deployments/962b8cc9-8697-46de-8452-ea01935d77d5/ai_service?version=2021-05-01"
    
    # Pega o JSON do Watson com segurança
    data = request.get_json(silent=True) or {}
    print(f"Dados recebidos do Watson: {data}") # Isso aparece nos logs da Vercel

    # Extrai o input do usuário (O Watson Assistant envia dentro de 'input')
    user_message = data.get("input", "")
    context = data.get("context", [])

    if not user_message:
        return jsonify({"response": "Erro: Não recebi texto no campo 'input'."}), 200

    try:
        # 1. Autenticação IAM
        iam_url = "https://iam.cloud.ibm.com/identity/token"
        auth_res = requests.post(iam_url, 
                                 data={"grant_type": "urn:ibm:params:oauth:grant-type:apikey", "apikey": api_key},
                                 headers={"Content-Type": "application/x-www-form-urlencoded"})
        auth_res.raise_for_status()
        access_token = auth_res.json().get("access_token")

        # 2. Chamada ao WatsonX (Formato exato de AI Service)
        headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
        
        # Estrutura padrão de payload para AI Service Deployments
        payload = {
            "input_data": [
                {
                    "values": [[user_message, context]]
                }
            ]
        }

        response = requests.post(url_watsonx, headers=headers, json=payload)
        
        # Se o WatsonX der erro, capturamos aqui sem derrubar o webhook
        if response.status_code != 200:
            print(f"Erro WatsonX: {response.text}")
            return jsonify({"response": "O modelo de IA está temporariamente indisponível."}), 200

        result = response.json()
        
        # Tenta extrair a resposta do labirinto de listas do WatsonX
        try:
            # O padrão comum é predictions[0] -> values[0] -> [0]
            assistant_reply = result['predictions'][0]['values'][0][0]
        except (KeyError, IndexError, TypeError):
            assistant_reply = "Recebi uma resposta, mas não consegui formatá-la."

        # 3. Retorno para o Watson Assistant
        return jsonify({
            "response": assistant_reply,
            "context": context + [{"role": "assistant", "content": assistant_reply}]
        })

    except Exception as e:
        print(f"Erro Geral: {str(e)}")
        return jsonify({"response": f"Ocorreu um erro interno: {str(e)}"}), 200

if __name__ == "__main__":
    app.run()
