# apps/news/filters.py
import django_filters
from .models import NewsArticle

class NewsArticleFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr='icontains')
    source = django_filters.CharFilter(lookup_expr='iexact')
    sentiment = django_filters.CharFilter(field_name='sentiment')
    category = django_filters.CharFilter(method='filter_category')
    tags = django_filters.CharFilter(method='filter_tags')
    date_from = django_filters.DateTimeFilter(field_name='published_at', lookup_expr='gte')
    date_to = django_filters.DateTimeFilter(field_name='published_at', lookup_expr='lte')

    class Meta:
        model = NewsArticle
        fields = [
            'title', 
            'source', 
            'sentiment', 
            'category', 
            'tags', 
            'date_from', 
            'date_to'
        ]

    def filter_category(self, queryset, name, value):
        return queryset.filter(categories__contains=[value])

    def filter_tags(self, queryset, name, value):
        return queryset.filter(tags__contains=[value])