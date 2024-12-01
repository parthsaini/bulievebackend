from django.db.models import Q 
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
    # queryset = Post.objects.all()
    # serializer_class = PostSerializer
    # permission_classes = [permissions.IsAuthenticatedOrReadOnly,IsOwnerOrReadOnly, 
    #     IsPostVisibleToUser]

    # def perform_create(self, serializer):
    #     serializer.save(user=self.request.user)

    # def get_queryset(self):
    #     # Filter posts based on visibility
    #     if self.request.user.is_authenticated:
    #         return Post.objects.filter(
    #             Q(visibility='public') | 
    #             Q(visibility='private', user=self.request.user) |
    #             Q(visibility='community', community__in=self.request.user.community_set.all())
    #         )
    #     return Post.objects.filter(visibility='public')



    queryset = Post.objects.all()
    serializer_class = PostSerializer
    #permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly, IsPostVisibleToUser]

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtering parameters
        community_id = self.request.query_params.get('community_id')
        username = self.request.query_params.get('username')
        visibility = self.request.query_params.get('visibility')
        tag = self.request.query_params.get('tag')
        
        # Base visibility filtering for authenticated/non-authenticated users
        if self.request.user.is_authenticated:
            queryset = queryset.filter(
                Q(visibility='public') | 
                Q(visibility='private', user=self.request.user) |
                Q(visibility='community', community__in=self.request.user.community_set.all())
            )
        else:
            queryset = queryset.filter(visibility='public')

        # Additional filtering options
        if community_id:
            queryset = queryset.filter(community_id=community_id)
        
        if username:
            queryset = queryset.filter(user__username=username)
        
        if visibility:
            queryset = queryset.filter(visibility=visibility)
        
        if tag:
            queryset = queryset.filter(tags__name=tag)
        
        return queryset

    @action(detail=False, methods=['GET'])
    def search(self, request):
        """
        Custom search action with multiple filtering options
        Query params:
        - q: search term (searches in title and content)
        - community_id: filter by community
        - username: filter by user
        - min_date: minimum creation date
        - max_date: maximum creation date
        - tags: comma-separated list of tags
        """
        queryset = self.get_queryset()
        
        # Search term
        search_query = request.query_params.get('q','')
        if search_query:
            queryset = queryset.filter(
               # Q(title__icontains=search_query) | 
                Q(content__icontains=search_query)
            )
        
        # Date range filtering
        min_date = request.query_params.get('min_date')
        max_date = request.query_params.get('max_date')
        
        if min_date:
            queryset = queryset.filter(created_at__gte=min_date)
        
        if max_date:
            queryset = queryset.filter(created_at__lte=max_date)
        
        # Multiple tag filtering
        tags = request.query_params.get('tags')
        if tags:
            tag_list = tags.split(',')
            queryset = queryset.filter(tags__name__in=tag_list)
        
        # Ordering
        ordering = request.query_params.get('ordering', '-created_at')
        queryset = queryset.order_by(ordering)
        
        # Pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
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