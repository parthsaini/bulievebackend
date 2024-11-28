from django.contrib import admin
from .models import NewsArticle

class NewsArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'source', 'published_at', 'sentiment')
    list_filter = ('published_at', 'sentiment', 'source')
    search_fields = ('title', 'content', 'tags')
    
    # Optional: customize how the JSON fields are displayed
    readonly_fields = ('categories', 'tags')
    
    def formatted_categories(self, obj):
        return ', '.join(obj.categories)
    formatted_categories.short_description = 'Categories'
    
    def formatted_tags(self, obj):
        return ', '.join(obj.tags)
    formatted_tags.short_description = 'Tags'

admin.site.register(NewsArticle, NewsArticleAdmin)