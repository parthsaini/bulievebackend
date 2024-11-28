from django.contrib import admin
from .models import Community, Post, Comment

class CommunityAdmin(admin.ModelAdmin):
    list_display = ('name', 'creator', 'created_at', 'is_private', 'member_count')
    list_filter = ('is_private', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'member_count')

class PostAdmin(admin.ModelAdmin):
    list_display = ('user', 'community', 'post_type', 'visibility', 'created_at')
    list_filter = ('post_type', 'visibility', 'created_at')
    search_fields = ('content', 'user__username')
    
    def formatted_media_urls(self, obj):
        return ', '.join(obj.media_urls)
    formatted_media_urls.short_description = 'Media URLs'

class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'created_at', 'parent_comment')
    list_filter = ('created_at',)
    search_fields = ('content', 'user__username')




from .models import CommunityMember

@admin.register(CommunityMember)
class CommunityMemberAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'community', 'role', 'joined_at']
    list_filter = ['role', 'joined_at']
    search_fields = ['user__username', 'community__name']
    readonly_fields = ['joined_at']    

admin.site.register(Community, CommunityAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)
