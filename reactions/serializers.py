from rest_framework import serializers
from .models import PostReaction

class PostReactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostReaction
        fields = ['id', 'post', 'user', 'reaction_type', 'created_at']
        read_only_fields = ['user', 'created_at']

    def create(self, validated_data):
        # Automatically set the user to the current authenticated user
        validated_data['user'] = self.context['request'].user
        
        # Check if user has already reacted to the post
        existing_reaction = PostReaction.objects.filter(
            post=validated_data['post'], 
            user=validated_data['user']
        ).first()
        
        if existing_reaction:
            # If reaction exists, update the existing reaction
            existing_reaction.reaction_type = validated_data['reaction_type']
            existing_reaction.save()
            return existing_reaction
        
        # Create a new reaction
        return PostReaction.objects.create(**validated_data)

    def validate(self, data):
        # Additional validation if needed
        return data