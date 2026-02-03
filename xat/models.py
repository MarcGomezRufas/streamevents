# xat/models.py
from django.db import models
from django.utils.timesince import timesince
from events.models import Event
from django.conf import settings

User = settings.AUTH_USER_MODEL

class XatMessage(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='xat_messages')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)
    is_highlighted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username}: {self.message[:50]}"

    def can_delete(self, user):
        if not user.is_authenticated:
            return False
        return user == self.user or user == self.event.creator or user.is_staff

    def get_user_display_name(self):
        return getattr(self.user, 'display_name', self.user.username) or self.user.username

    def get_time_since(self):
        return timesince(self.created_at).split(',')[0] + " ago"

    class Meta:
        ordering = ['created_at']
        verbose_name = 'Missatge de Xat'
        verbose_name_plural = 'Missatges de Xat'