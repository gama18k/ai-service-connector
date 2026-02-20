from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route('/api/index', methods=['POST', 'GET'])
@app.route('/', methods=['POST', 'GET'])
def webhook_route():
    if request.method == 'GET':
        return "Webhook RAG está Online!", 200

    api_key = "bmajj8krZddh16ifk0ymnVdqzeamOL1JZ9dd0lC_v5c0"
    url_watsonx = "https://au-syd.ml.cloud.ibm.com/ml/v4/deployments/a677b473-d0eb-4e5f-bf96-5f9ee7eef543/ai_service?version=2021-05-01"
    
    # 1. Pega o JSON cru que o Watson Assistant enviou
    data = request.get_json(silent=True) or {}
    
    # =========================================================
    # 2. MODO ESPIÃO: Imprime os dados nos logs da Vercel
    # O "flush=True" garante que o log apareça na hora no painel
    print("=== DADOS RECEBIDOS DO WATSON ===", flush=True)
    print(data, flush=True)
    print("=================================", flush=True)
    # =========================================================

    # 3. Tenta extrair a mensagem e o contexto
    user_message = data.get("input", "")
    context = data.get("context", [])

    if not user_message:
        return jsonify({"response": "Erro: Campo 'input' não encontrado."}), 200

    try:
        # Autenticação IAM
        iam_res = requests.post("https://iam.cloud.ibm.com/identity/token", 
                                 data={"grant_type": "urn:ibm:params:oauth:grant-type:apikey", "apikey": api_key},
                                 headers={"Content-Type": "application/x-www-form-urlencoded"})
        iam_res.raise_for_status()
        access_token = iam_res.json().get("access_token")

        # Chamada WatsonX
        headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
# Adicionamos os "fields" para o RAG saber quem é quem
        payload = {
            "input_data": [
                {
                    "fields": ["input", "context"],
                    "values": [[user_message, context]]
                }
            ]
        }
        response = requests.post(url_watsonx, headers=headers, json=payload)
        
        if response.status_code != 200:
            return jsonify({"response": f"O modelo de IA retornou erro: {response.text}"}), 200

        result = response.json()
        
        try:
            assistant_reply = result['predictions'][0]['values'][0][0]
        except:
            assistant_reply = f"Não consegui formatar a resposta. O WatsonX devolveu: {result}"

        return jsonify({
            "response": assistant_reply,
            "context": context + [{"role": "assistant", "content": assistant_reply}]
        })

    except Exception as e:
        return jsonify({"response": f"Erro interno: {str(e)}"}), 200



