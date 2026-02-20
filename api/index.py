from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route('/', methods=['POST', 'GET'])
@app.route('/api/index', methods=['POST', 'GET'])
def handler():
    # Caso receba um GET acidental (navegador), não dá erro 405
    if request.method == 'GET':
        return "Webhook ativo!", 200

    # 1. Configurações
    api_key = "htVumjBHrdw_0JMZ1TJCZnn0ZKf2ew9OP4QBAGNr32R9"
    url_watsonx = "https://au-syd.ml.cloud.ibm.com/ml/v4/deployments/962b8cc9-8697-46de-8452-ea01935d77d5/ai_service?version=2021-05-01"
    
    # 2. Extração segura dos dados
    data = request.get_json(silent=True) or {}
    
    # O Watson Assistant às vezes coloca os parâmetros dentro de 'input' ou direto na raiz
    user_message = data.get("input", "")
    context = data.get("context", [])

    if not user_message:
        return jsonify({"response": "Erro: Mensagem vazia recebida pelo webhook."}), 200

    try:
        # --- Autenticação IAM ---
        iam_url = "https://iam.cloud.ibm.com/identity/token"
        token_res = requests.post(iam_url, 
                                 data={"grant_type": "urn:ibm:params:oauth:grant-type:apikey", "apikey": api_key},
                                 headers={"Content-Type": "application/x-www-form-urlencoded"})
        token_res.raise_for_status()
        access_token = token_res.json().get("access_token")

        # --- Chamada WatsonX ---
        headers_rag = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
        
        # Ajuste o payload para o formato exato que seu AI Service espera
        payload_rag = {
            "input_data": [{"values": [[user_message, context]]}]
        }

        response = requests.post(url_watsonx, headers=headers_rag, json=payload_rag)
        
        if response.status_code != 200:
            return jsonify({"response": f"Erro no WatsonX: {response.text}"}), 200

        result = response.json()
        
        # Tentativa de extração da resposta
        try:
            assistant_reply = result['predictions'][0]['values'][0][0]
        except (KeyError, IndexError):
            assistant_reply = "O modelo processou, mas o formato de saída foi inesperado."

        return jsonify({
            "response": assistant_reply,
            "context": context + [{"role": "assistant", "content": assistant_reply}]
        })

    except Exception as e:
        # Retornamos 200 com a mensagem de erro para o Watson não "travar" o fluxo
        return jsonify({"response": f"Erro interno no Webhook: {str(e)}"}), 200
