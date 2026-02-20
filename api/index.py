from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Mudamos o nome da função de "handler" para "webhook_route" para a Vercel não bugar
@app.route('/api/index', methods=['POST', 'GET'])
@app.route('/', methods=['POST', 'GET'])
def webhook_route():
    if request.method == 'GET':
        return "Webhook RAG está Online!", 200

    api_key = "htVumjBHrdw_0JMZ1TJCZnn0ZKf2ew9OP4QBAGNr32R9"
    url_watsonx = "https://au-syd.ml.cloud.ibm.com/ml/v4/deployments/962b8cc9-8697-46de-8452-ea01935d77d5/ai_service?version=2021-05-01"
    
    data = request.get_json(silent=True) or {}
    user_message = data.get("input", "")
    context = data.get("context", [])

    if not user_message:
        return jsonify({"response": "Erro: Campo 'input' não encontrado."}), 200

    try:
        # 1. Autenticação IAM
        iam_res = requests.post("https://iam.cloud.ibm.com/identity/token", 
                                 data={"grant_type": "urn:ibm:params:oauth:grant-type:apikey", "apikey": api_key},
                                 headers={"Content-Type": "application/x-www-form-urlencoded"})
        iam_res.raise_for_status()
        access_token = iam_res.json().get("access_token")

        # 2. Chamada WatsonX
        headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
        payload = {"input_data": [{"values": [[user_message, context]]}]}

        response = requests.post(url_watsonx, headers=headers, json=payload)
        
        if response.status_code != 200:
            return jsonify({"response": "O modelo de IA não respondeu corretamente."}), 200

        result = response.json()
        
        try:
            assistant_reply = result['predictions'][0]['values'][0][0]
        except:
            assistant_reply = "Não consegui formatar a resposta da IA."

        return jsonify({
            "response": assistant_reply,
            "context": context + [{"role": "assistant", "content": assistant_reply}]
        })

    except Exception as e:
        return jsonify({"response": f"Erro interno: {str(e)}"}), 200
