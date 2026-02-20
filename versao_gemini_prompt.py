import requests
import time

def main(args):
    # 1. Configurações Iniciais
    api_key = "htVumjBHrdw_0JMZ1TJCZnn0ZKf2ew9OP4QBAGNr32R9"
    url = "https://au-syd.ml.cloud.ibm.com/ml/v4/deployments/962b8cc9-8697-46de-8452-ea01935d77d5/ai_service?version=2021-05-01"
    
    # Captura a mensagem do usuário vinda do Watson Assistant
    user_message = args.get("input", "")
    # Captura o histórico/contexto anterior (se existir)
    context = args.get("context", [])

    if not user_message:
        return {"error": "Nenhuma mensagem enviada."}

    try:
        # --- 1. Autenticação com o IAM para obter token ---
        iam_url = "https://iam.cloud.ibm.com/identity/token"
        headers_iam = {"Content-Type": "application/x-www-form-urlencoded"}
        data_iam = {
            "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
            "apikey": api_key
        }
        
        token_res = requests.post(iam_url, headers=headers_iam, data=data_iam)
        token_res.raise_for_status()
        access_token = token_res.json().get("access_token")

        # --- 2. Registro da nova mensagem do usuário no contexto ---
        context.append({"role": "user", "content": user_message})

        # --- 3. Chamada ao endpoint do WatsonX (RAG) ---
        headers_rag = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        # O payload depende de como seu AI Service foi definido. 
        # Geralmente segue este padrão para deployments de AI Service:
        payload_rag = {
            "input_data": [
                {
                    "values": [[user_message, context]]
                }
            ]
        }

        response = requests.post(url, headers=headers_rag, json=payload_rag)
        response.raise_for_status()
        
        # Extração da resposta (ajuste o parsing conforme o retorno do seu deploy)
        result = response.json()
        assistant_reply = result['predictions'][0]['values'][0][0]

        # --- 4. Registro da resposta do assistente no contexto ---
        context.append({"role": "assistant", "content": assistant_reply})

        # --- 5. Retorno da resposta final para o Watson Assistant ---
        return {
            "response": assistant_reply,
            "context": context
        }

    except Exception as e:
        return {"error": str(e)}