# events/models.py
from django.db import models
from djongo import models as djongo_models
from django.urls import reverse
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import re

User = settings.AUTH_USER_MODEL

CATEGORY_CHOICES = [
    ('gaming', 'Gaming'),
    ('music', 'Música'),
    ('talk', 'Xerrades'),
    ('education', 'Educació'),
    ('sports', 'Esports'),
    ('entertainment', 'Entreteniment'),
    ('technology', 'Tecnologia'),
    ('art', 'Art i Creativitat'),
    ('other', 'Altres'),
]

STATUS_CHOICES = [
    ('scheduled', 'Programat'),
    ('live', 'En Directe'),
    ('finished', 'Finalitzat'),
    ('cancelled', 'Cancel·lat'),
]

class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='events')
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES)
    scheduled_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    thumbnail = models.ImageField(upload_to='events/thumbnails/', blank=True, null=True)
    max_viewers = models.PositiveIntegerField(default=100)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    tags = models.CharField(max_length=500, blank=True, null=True, help_text="Separades per comes")
    stream_url = models.URLField(max_length=500, blank=True, null=True)

    CATEGORY_DURATIONS = {
        'gaming': 180,
        'music': 90,
        'talk': 60,
        'education': 120,
        'sports': 150,
        'entertainment': 120,
        'technology': 90,
        'art': 120,
        'other': 90,
    }

    embedding = models.TextField(blank=True, null=True)  # Stores JSON list of floats
    embedding_model = models.CharField(max_length=200, blank=True, null=True)
    embedding_updated_at = models.DateTimeField(blank=True, null=True)


    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Esdeveniment'
        verbose_name_plural = 'Esdeveniments'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('events:event_detail', args=[self.pk])

    @property
    def is_live(self):
        now = timezone.now()
        if self.status == 'live':
            return True
        if self.status == 'scheduled' and self.scheduled_date <= now:
            duration = self.CATEGORY_DURATIONS.get(self.category, 90)
            end_time = self.scheduled_date + timedelta(minutes=duration)
            return now <= end_time
        return False

    @property
    def is_upcoming(self):
        return self.status == 'scheduled' and self.scheduled_date > timezone.now()

    def get_duration(self):
        """Retorna la durada prevista en minuts segons la categoria."""
        return self.CATEGORY_DURATIONS.get(self.category, 90)

    def get_tags_list(self):
        if not self.tags:
            return []
        return [t.strip() for t in self.tags.split(',') if t.strip()]

    def get_stream_embed_url(self):
        if not self.stream_url:
            return None

        url = self.stream_url.strip()

        # YouTube
        if 'youtube.com' in url or 'youtu.be' in url:
            yt_match = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11})', url)
            if yt_match:
                vid = yt_match.group(1)
                return f"https://www.youtube.com/embed/{vid}"
            return None

        # Twitch
        if 'twitch.tv' in url:
            tw_match = re.search(r'twitch\.tv\/([A-Za-z0-9_]+)', url)
            if tw_match:
                channel = tw_match.group(1)
                # ⚠️ Canvia 'localhost' pel teu domini en producció
                return f"https://player.twitch.tv/?channel={channel}&parent=localhost"
        return None