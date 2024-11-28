from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the owner of the post
        return obj.user == request.user

class IsPostVisibleToUser(permissions.BasePermission):
    """
    Custom permission to check post visibility.
    """
    def has_object_permission(self, request, view, obj):
        # Public posts are always visible
        if obj.visibility == 'public':
            return True
        
        # For private posts, only the owner can view
        if obj.visibility == 'private':
            return obj.user == request.user
        
        # For community posts, check if user is a community member
        if obj.visibility == 'community':
            if not obj.community:
                return False
            
            from .models import CommunityMember
            return CommunityMember.objects.filter(
                community=obj.community, 
                user=request.user
            ).exists()
        
        return False