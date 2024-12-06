from rest_framework import serializers
from django.conf import settings
from .models import Community, Post, Comment, CommunityMember
from django.contrib.auth import get_user_model
from reactions.models import PostReaction
from reactions.serializers import PostReactionSerializer
User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class CommunitySerializer(serializers.ModelSerializer):
    creator = UserSerializer(read_only=True)
    creator_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), 
        source='creator', 
        write_only=True
    )

    class Meta:
        model = Community
        fields = [
            'id', 'name', 'description', 'creator', 
            'creator_id', 'created_at', 'is_private', 
            'member_count','community_photo'
        ]
        read_only_fields = ['created_at', 'member_count','is_private']
        extra_kwargs = {
            'community_photo': {'required': False}
        }
    def create(self, validated_data):
        # If a creator is provided in the context (typically from frontend), use that
        creator = validated_data.get('creator') or self.context['request'].user
        
        # Update validated_data with the creator
        validated_data['creator'] = creator
        
        # Create the community
        return Community.objects.create(**validated_data)
    def update(self, instance, validated_data):
        """
        Custom update method to handle photo upload
        """
        # Remove creator from validated data if present to prevent accidental changes
        validated_data.pop('creator', None)
        
        return super().update(instance, validated_data)




class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), 
        source='user', 
        write_only=True
    )
    parent_comment_id = serializers.PrimaryKeyRelatedField(
        queryset=Comment.objects.all(), 
        source='parent_comment', 
        required=False,
        allow_null=True
    )

    class Meta:
        model = Comment
        fields = [
            'id', 'post', 'user', 'user_id', 
            'parent_comment', 'parent_comment_id', 
            'content', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def create(self, validated_data):
        # If a user is provided in the context (typically from frontend), use that
        user = validated_data.get('user') or self.context['request'].user
        
        # Update validated_data with the user
        validated_data['user'] = user
        
        # Create the comment
        return Comment.objects.create(**validated_data)

class PostSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), 
        source='user', 
        write_only=True
    )
    comments = CommentSerializer(many=True, read_only=True)
    comments_count = serializers.SerializerMethodField()
    reactions = serializers.SerializerMethodField()
    reactions_count = serializers.SerializerMethodField()  # Add this line
    class Meta:
        model = Post
        fields = [
            'id', 'user', 'user_id', 'community', 
            'content', 'media_urls', 'created_at', 
            'updated_at', 'post_type', 'visibility',
            'comments','comments_count', 'reactions','reactions_count'  # Add reactions_count here
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_comments_count(self, obj):
        return obj.comments.count()

    def get_reactions(self, obj):
        # Get all reactions for this post
        reactions = PostReaction.objects.filter(post=obj)
        return PostReactionSerializer(reactions, many=True).data

    def get_reactions_count(self, obj):
        # Count the total number of reactions for this post
        return PostReaction.objects.filter(post=obj).count()

class CommunityMemberSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    community_name = serializers.CharField(source='community.name', read_only=True)

    class Meta:
        model = CommunityMember
        fields = ['id', 'community', 'user', 'username', 'community_name', 'role', 'joined_at']
        read_only_fields = [ 'joined_at']

    def create(self, validated_data):
        # Automatically set the user to the current authenticated user
        user = validated_data.get('user') or self.context['request'].user
        
        # Update validated_data with the user
        validated_data['user'] = user
        
        # Increment community member count
        community = validated_data['community']
        community.member_count += 1
        community.save()
        
        return CommunityMember.objects.create(**validated_data)

    def validate(self, data):
        # Prevent joining the same community twice
        request = self.context.get('request')
        community = data.get('community')
        
        if request and community:
            existing_member = CommunityMember.objects.filter(
                community=community, 
                user=request.user
            ).exists()
            
            if existing_member:
                raise serializers.ValidationError("You are already a member of this community.")
        
        return data