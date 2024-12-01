# apps/news/views.py
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import NewsArticle
from .serializers import (
    NewsArticleSerializer, 
    NewsArticleCreateSerializer, 
    NewsArticleUpdateSerializer
)
from .filters import NewsArticleFilter


from drf_spectacular.utils import extend_schema

@extend_schema(tags=['News'])
class NewsArticleViewSet(viewsets.ModelViewSet):
    queryset = NewsArticle.objects.all().order_by('-published_at')
    serializer_class = NewsArticleSerializer
    #permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = NewsArticleFilter
    search_fields = ['title', 'content', 'source', 'tags']
    ordering_fields = ['published_at', 'title', 'source']

    def get_serializer_class(self):
        if self.action == 'create':
            return NewsArticleCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return NewsArticleUpdateSerializer
        return NewsArticleSerializer

    @action(detail=False, methods=['GET'], url_path='by-sentiment')
    def articles_by_sentiment(self, request):
        sentiment = request.query_params.get('sentiment', None)
        if sentiment:
            articles = self.queryset.filter(sentiment=sentiment)
            serializer = self.get_serializer(articles, many=True)
            return Response(serializer.data)
        return Response(
            {"error": "Sentiment parameter is required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=False, methods=['GET'], url_path='by-category')
    def articles_by_category(self, request):
        category = request.query_params.get('category', None)
        if category:
            articles = self.queryset.filter(categories__contains=[category])
            serializer = self.get_serializer(articles, many=True)
            return Response(serializer.data)
        return Response(
            {"error": "Category parameter is required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=True, methods=['POST'], url_path='add-categories')
    def add_categories(self, request, pk=None):
        article = self.get_object()
        categories = request.data.get('categories', [])
        
        if not isinstance(categories, list):
            return Response(
                {"error": "Categories must be a list"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Add new categories, avoiding duplicates
        existing_categories = article.categories
        updated_categories = list(set(existing_categories + categories))
        
        article.categories = updated_categories
        article.save()
        
        serializer = self.get_serializer(article)
        return Response(serializer.data)