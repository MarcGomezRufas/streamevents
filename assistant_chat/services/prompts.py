import json


def build_prompt(user_message, candidates):
    """
    Construeix el prompt per al LLM amb el context d'events reals.
    candidates: [{id, title, scheduled_date, category, tags, url, score}, ...]
    """
    context_json = json.dumps(candidates, ensure_ascii=False, indent=2)

    return f"""Ets un assistent que recomana esdeveniments del lloc StreamEvents.
IMPORTANT:
- NOMES pots recomanar esdeveniments que apareguin al CONTEXT.
- No inventis esdeveniments, dates, ni URLs.
- Si no hi ha cap esdeveniment adequat, digues-ho i demana aclariments.
- Respon SEMPRE en catala.

Respon en aquest format JSON EXACTE (sense text addicional fora del JSON):

{{
  "answer": "text curt amb la teva recomanacio",
  "recommended_ids": [1, 2, 3],
  "follow_up": "pregunta opcional per afinar la cerca (o string buit)"
}}

CONTEXT (llista d'esdeveniments disponibles):
{context_json}

Peticio de l'usuari: {user_message}"""
