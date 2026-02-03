from django.core.management.base import BaseCommand
from django.utils import timezone

from events.models import Event
from semantic_search.services.embeddings import embed_text, model_name

import json

class Command(BaseCommand):
    help = "Genera i desa embeddings per a Events."

    def add_arguments(self, parser):
        parser.add_argument("--force", action="store_true", help="Recalcula encara que ja hi hagi embedding")
        parser.add_argument("--limit", type=int, default=0, help="Limita el nombre d'events (0 = tots)")

    def handle(self, *args, **options):
        force = options["force"]
        limit = options["limit"]

        qs = Event.objects.all()
        # Nota: per a strings no podem fer isnull=True exactament igual si est? buit, per? ho intentem
        if not force:
            # Filtrem si est? buit o null
            qs = qs.filter(embedding__isnull=True)

        # Si volem iterar python millor si hi ha db errors
        # Pero qs[:limit] sol anar b?
        if limit and limit > 0:
            qs = qs[:limit]

        total = 0
        for e in qs:
            # Check manual pq el filter string pot fallar en alguns backends
            if not force and e.embedding:
                continue

            text = " | ".join([
                (e.title or "").strip(),
                (e.description or "").strip(),
                (e.category or "").strip(),
                (e.tags or "").strip(),
            ]).strip()

            if not text:
                continue

            vec = embed_text(text)
            e.embedding = json.dumps(vec)  # DESEM COM A STRING
            e.embedding_model = model_name()
            e.embedding_updated_at = timezone.now()
            e.save(update_fields=["embedding", "embedding_model", "embedding_updated_at"])
            total += 1

        self.stdout.write(self.style.SUCCESS(f"Embeddings generats: {total}"))
