import json
import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.1:8b"
# 


def generate(prompt):
    """
    Envia un prompt al model Ollama local i retorna la resposta.
    """
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.3,
            "top_p": 0.9,
            "num_ctx": 2048,
        },
    }
    try:
        r = requests.post(OLLAMA_URL, json=payload, timeout=120)
        r.raise_for_status()
        data = r.json()
        return data.get("response", "").strip()
    except requests.exceptions.ConnectionError:
        return json.dumps({
            "answer": "No s'ha pogut connectar amb el model Ollama. Assegura't que està engegat (ollama serve).",
            "recommended_ids": [],
            "follow_up": "",
        })
    except requests.exceptions.Timeout:
        return json.dumps({
            "answer": "El model ha trigat massa a respondre. Prova amb una consulta més curta.",
            "recommended_ids": [],
            "follow_up": "",
        })
    except Exception as exc:
        return json.dumps({
            "answer": f"Error inesperat: {exc}",
            "recommended_ids": [],
            "follow_up": "",
        })
