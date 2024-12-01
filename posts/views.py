from django.db.models import Q 
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, permissions, status
from .models import Community, Post, Comment, CommunityMember
from .serializers import (
    CommunitySerializer, 
    PostSerializer, 
    CommentSerializer,
    CommunityMemberSerializer
)
from .permissions import IsOwnerOrReadOnly, IsPostVisibleToUser

from drf_spectacular.utils import extend_schema
from django.contrib.auth import get_user_model
from rest_framework.parsers import MultiPartParser, FormParser
User = get_user_model()




@extend_schema(tags=['Communities'])
class CommunityViewSet(viewsets.ModelViewSet):
    queryset = Community.objects.all()
    serializer_class = CommunitySerializer
   #permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    parser_classes = [MultiPartParser, FormParser]  # Add support for file uploads
    
    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

    @action(detail=True, methods=['POST'], 
            parser_classes=[MultiPartParser, FormParser])
    def upload_photo(self, request, pk=None):
        """
        Upload a photo for a specific community
        """
        community = self.get_object()
        
        # Check if the current user is the creator or an admin
        is_creator = community.creator == request.user
        is_admin = CommunityMember.objects.filter(
            community=community, 
            user=request.user, 
            role__in=['admin', 'moderator']
        ).exists()
        
        if not (is_creator or is_admin):
            return Response(
                {"error": "You are not authorized to upload a community photo"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check if photo is in request
        if 'community_photo' not in request.FILES:
            return Response(
                {"error": "No photo uploaded"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Save the photo
        community.community_photo = request.FILES['community_photo']
        community.save()
        
        # Serialize and return the updated community
        serializer = self.get_serializer(community)
        return Response(serializer.data)

    @action(detail=True, methods=['DELETE'])
    def remove_photo(self, request, pk=None):
        """
        Remove the community photo
        """
        community = self.get_object()
        
        # Check if the current user is the creator or an admin
        is_creator = community.creator == request.user
        is_admin = CommunityMember.objects.filter(
            community=community, 
            user=request.user, 
            role__in=['admin', 'moderator']
        ).exists()
        
        if not (is_creator or is_admin):
            return Response(
                {"error": "You are not authorized to remove the community photo"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Remove the photo
        if community.community_photo:
            community.community_photo.delete()
        
        community.save()
        
        return Response(
            {"message": "Community photo removed successfully"},
            status=status.HTTP_200_OK
        )

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
        post_type = self.request.query_params.get('post_type')
        
        # Base visibility filtering for authenticated/non-authenticated users
        if self.request.user.is_authenticated:
            print (self.request.user)
            queryset = queryset.filter(
                Q(visibility='public') | 
                Q(visibility='private', user=self.request.user) |
                Q(visibility='community', community__in=self.request.user.community_set.all())
            )
        else:
            print (self.request.user)
            queryset = queryset.filter(visibility='public')

        # Additional filtering options
        if community_id:
            queryset = queryset.filter(community_id=community_id)
        
        if username:
            
            try:
                user = User.objects.get(email=username)
                queryset = queryset.filter(user=user)
            except User.DoesNotExist:
                # Return empty queryset if user not found
                print ("doesn't exit")
                return Post.objects.none()
        
        if visibility:
            queryset = queryset.filter(visibility=visibility)
        
        if post_type:
            queryset = queryset.filter(post_type=post_type)
        
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