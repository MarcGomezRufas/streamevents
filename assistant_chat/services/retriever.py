import json
from django.utils import timezone
from events.models import Event
from semantic_search.services.embeddings import embed_text
from semantic_search.services.ranker import cosine_top_k


def build_event_text(e):
    """Construeix el text representatiu d'un event."""
    return " | ".join([
        (e.title or "").strip(),
        (e.description or "").strip(),
        (e.category or "").strip(),
        (e.tags or "").strip(),
    ]).strip()


def retrieve_events(query, only_future=True, k=8):
    """
    Recupera els top-K events més rellevants per a la query donada,
    fent servir embeddings i cosine similarity.
    """
    q_vec = embed_text(query)
    if not q_vec:
        return []

    qs = Event.objects.all()
    if only_future:
        qs = qs.filter(scheduled_date__gte=timezone.now())

    items = []
    for e in qs:
        raw_emb = getattr(e, "embedding", None)
        if not raw_emb:
            continue

        # Descodifiquem JSON si és string (TextField)
        try:
            if isinstance(raw_emb, str):
                emb = json.loads(raw_emb)
            else:
                emb = raw_emb
            if isinstance(emb, list) and len(emb) > 0:
                items.append((e, emb))
        except (json.JSONDecodeError, TypeError):
            continue

    ranked = cosine_top_k(q_vec, items, k=max(k, 20))

    # Llindar minim per evitar recomanar qualsevol cosa
    ranked = [(e, s) for (e, s) in ranked if s >= 0.15]

    return ranked[:k]
