from django.db import models
from django.conf import settings
from posts.models import Post

class PostReaction(models.Model):
    REACTION_TYPES = [
        ('like', 'Like'),
        ('love', 'Love'),
        ('insight', 'Insight'),
        ('disagree', 'Disagree'),
        ('surprised', 'Surprised')
    ]

    post = models.ForeignKey(
        Post, 
        on_delete=models.CASCADE, 
        related_name='reactions'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE
    )
    reaction_type = models.CharField(
        max_length=20, 
        choices=REACTION_TYPES
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post', 'user')

