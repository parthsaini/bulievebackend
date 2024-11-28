# apps/news/serializers.py
from rest_framework import serializers
from .models import NewsArticle

class NewsArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsArticle
        fields = [
            'id', 
            'title', 
            'source', 
            'original_url', 
            'published_at', 
            'content', 
            'ai_summary', 
            'categories', 
            'sentiment', 
            'tags'
        ]
        read_only_fields = ['id']

class NewsArticleCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsArticle
        fields = [
            'title', 
            'source', 
            'original_url', 
            'published_at', 
            'content', 
            'ai_summary', 
            'categories', 
            'sentiment', 
            'tags'
        ]

class NewsArticleUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsArticle
        fields = [
            'title', 
            'source', 
            'original_url', 
            'content', 
            'ai_summary', 
            'categories', 
            'sentiment', 
            'tags'
        ]