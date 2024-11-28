from django.contrib import admin
from .models import PostReaction

@admin.register(PostReaction)
class PostReactionAdmin(admin.ModelAdmin):
    list_display = ['id', 'post', 'user', 'reaction_type', 'created_at']
    list_filter = ['reaction_type', 'created_at']
    search_fields = ['user__username', 'post__id']
    readonly_fields = ['created_at']