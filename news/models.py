from django.db import models
from django.conf import settings

# Create your models here.
class NewsArticle(models.Model):
    SENTIMENT_CHOICES = [
        ('positive', 'Positive'),
        ('negative', 'Negative'),
        ('neutral', 'Neutral')
    ]

    title = models.CharField(max_length=500)
    source = models.CharField(max_length=200)
    original_url = models.URLField(max_length=1000)
    published_at = models.DateTimeField()
    content = models.TextField()
    ai_summary = models.TextField(blank=True)
    categories = models.JSONField(default=list)
    sentiment = models.CharField(
        max_length=20, 
        choices=SENTIMENT_CHOICES, 
        null=True, 
        blank=True
    )
    tags = models.JSONField(default=list)

    def __str__(self):
        return self.title