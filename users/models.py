from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    display_name = models.CharField(max_length=100, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    def __str__(self):
        return self.username

class Follow(models.Model):
    # follower (A) segueix following (B)
    follower = models.ForeignKey(
        'CustomUser',
        related_name='following_set',
        on_delete=models.CASCADE
    )
    following = models.ForeignKey(
        'CustomUser',
        related_name='followers_set',
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'following')  # Evita duplicats A->B

    def __str__(self):
        return f'{self.follower} -> {self.following}'