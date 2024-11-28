from django.db import models
from django.conf import settings

class Community(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_private = models.BooleanField(default=False)
    member_count = models.PositiveIntegerField(default=0)


    def update_member_count(self):
        """
        Manually update the member count based on actual community members.
        """
        self.member_count = self.members.count()
        self.save(update_fields=['member_count'])

    def __str__(self):
        return self.name

class Post(models.Model):
    POST_TYPES = [
        ('text', 'Text'),
        ('link', 'Link'),
        ('image', 'Image'),
        ('video', 'Video'),
        ('financial_analysis', 'Financial Analysis')
    ]

    VISIBILITY_TYPES = [
        ('public', 'Public'),
        ('private', 'Private'),
        ('community', 'Community')
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE
    )
    community = models.ForeignKey(
        Community, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    content = models.TextField()
    media_urls = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    post_type = models.CharField(
        max_length=20, 
        choices=POST_TYPES
    )
    visibility = models.CharField(
        max_length=20, 
        choices=VISIBILITY_TYPES, 
        default='public'
    )

    def __str__(self):
        return f"Post by {self.user.username}"

class Comment(models.Model):
    post = models.ForeignKey(
        Post, 
        on_delete=models.CASCADE, 
        related_name='comments'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE
    )
    parent_comment = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Comment by {self.user.username}"

class CommunityMember(models.Model):
    ROLE_CHOICES = [
        ('member', 'Member'),
        ('admin', 'Admin'),
        ('moderator', 'Moderator')
    ]

    community = models.ForeignKey(
        Community, 
        on_delete=models.CASCADE,
        related_name='members'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE
    )
    role = models.CharField(
        max_length=20, 
        choices=ROLE_CHOICES, 
        default='member'
    )
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('community', 'user')

    def save(self, *args, **kwargs):
        """
        Override save method to update community member count.
        """
        is_new = self._state.adding
        super().save(*args, **kwargs)
        
        if is_new:
            self.community.update_member_count()

    def delete(self, *args, **kwargs):
        """
        Override delete method to update community member count.
        """
        community = self.community
        super().delete(*args, **kwargs)
        community.update_member_count()

    def __str__(self):
        return f"{self.user.username} - {self.community.name}"