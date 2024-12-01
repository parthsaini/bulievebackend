
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, permissions
from .models import Community, Post, Comment, CommunityMember
from .serializers import (
    CommunitySerializer, 
    PostSerializer, 
    CommentSerializer,
    CommunityMemberSerializer
)
from .permissions import IsOwnerOrReadOnly, IsPostVisibleToUser

from drf_spectacular.utils import extend_schema





@extend_schema(tags=['Communities'])
class CommunityViewSet(viewsets.ModelViewSet):
    queryset = Community.objects.all()
    serializer_class = CommunitySerializer
    #permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

@extend_schema(tags=['Posts'])
class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    #permission_classes = [permissions.IsAuthenticatedOrReadOnly,IsOwnerOrReadOnly, 
       # IsPostVisibleToUser]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        # Filter posts based on visibility
        if self.request.user.is_authenticated:
            return Post.objects.filter(
                Q(visibility='public') | 
                Q(visibility='private', user=self.request.user) |
                Q(visibility='community', community__in=self.request.user.community_set.all())
            )
        return Post.objects.filter(visibility='public')

@extend_schema(tags=['Comments'])
class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    #permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

@extend_schema(tags=['Community-Members'])
class CommunityMemberViewSet(viewsets.ModelViewSet):
    queryset = CommunityMember.objects.all()
    serializer_class = CommunityMemberSerializer
    #permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Filter members by community if community_id is provided
        community_id = self.request.query_params.get('community_id')
        if community_id:
            return self.queryset.filter(community_id=community_id)
        return self.queryset

    @action(detail=False, methods=['POST'])
    def join_community(self, request):
        # Custom action to join a community
        community_id = request.data.get('community_id')
        
        try:
            community = Community.objects.get(id=community_id)
        except Community.DoesNotExist:
            return Response({'detail': 'Community not found.'}, status=404)
        
        # Check if community is private and handle accordingly
        if community.is_private:
            return Response({'detail': 'This is a private community. Request to join is required.'}, status=403)
        
        # Create membership
        serializer = self.get_serializer(data={'community': community_id})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(serializer.data, status=201)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Only allow leaving or removal by community admin or the member themselves
        if (instance.user != request.user and 
            not CommunityMember.objects.filter(
                community=instance.community, 
                user=request.user, 
                role__in=['admin', 'moderator']
            ).exists()):
            return Response({'detail': 'Not authorized to remove this member.'}, status=403)
        
        # Decrement community member count
        community = instance.community
        community.member_count -= 1
        community.save()
        
        self.perform_destroy(instance)
        return Response(status=204)