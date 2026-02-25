import json
import re
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from .services.retriever import retrieve_events
from .services.prompts import build_prompt
from .services.llm_ollama import generate


def chat_page(request):
    """Renderitza la pagina del xat."""
    return render(request, "assistant_chat/chat.html")


@csrf_exempt
def chat_api(request):
    """
    API endpoint del xat.
    POST /assistant/api/chat/
    Body: {"message": "...", "only_future": true}
    """
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)

    try:
        payload = json.loads(request.body.decode("utf-8"))
    except Exception:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    message = (payload.get("message") or "").strip()
    only_future = bool(payload.get("only_future", True))

    if not message:
        return JsonResponse({"error": "Empty message"}, status=400)

    # 1. Retrieval: obtenim events candidats amb semantic search
    ranked = retrieve_events(message, only_future=only_future, k=8)

    # 2. Preparem candidats per al context del LLM
    candidates = []
    for e, score in ranked:
        candidates.append({
            "id": int(e.pk),
            "title": e.title,
            "scheduled_date": e.scheduled_date.isoformat() if e.scheduled_date else None,
            "category": e.category,
            "tags": e.tags or "",
            "url": e.get_absolute_url(),
            "score": round(float(score), 3),
        })

    # 3. Construim prompt i cridem el LLM
    prompt = build_prompt(message, candidates)
    llm_text = generate(prompt)

    # 4. Parsegem la resposta JSON del model
    llm_json = _parse_llm_response(llm_text, candidates)

    # 5. Filtrem recommended_ids perque nomes siguin dels candidats reals
    allowed = {c["id"] for c in candidates}
    rec_ids = [i for i in llm_json.get("recommended_ids", []) if i in allowed]

    # 6. Preparem cards finals
    cards = [c for c in candidates if c["id"] in rec_ids]
    if not cards and candidates:
        # Fallback: si el model no n'ha seleccionat cap, agafa top-3
        cards = candidates[:3]

    return JsonResponse({
        "answer": llm_json.get("answer", ""),
        "follow_up": llm_json.get("follow_up", ""),
        "events": cards,
    })


def _parse_llm_response(llm_text, candidates):
    """
    Intenta parsear la resposta del LLM com a JSON.
    Amb fallback robust si el model no respecta el format.
    """
    # Primer intentem parsear directament
    try:
        return json.loads(llm_text)
    except (json.JSONDecodeError, TypeError):
        pass

    # Intentem extreure un bloc JSON del text
    json_match = re.search(r'\{[\s\S]*\}', llm_text)
    if json_match:
        try:
            return json.loads(json_match.group())
        except (json.JSONDecodeError, TypeError):
            pass

    # Fallback segur
    return {
        "answer": llm_text if llm_text else "No he pogut generar una resposta estructurada. Prova amb una consulta mes concreta.",
        "recommended_ids": [c["id"] for c in candidates[:3]],
        "follow_up": "",
    }
