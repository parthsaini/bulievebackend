from rest_framework import viewsets, permissions
from rest_framework.response import Response
from .models import PostReaction
from .serializers import PostReactionSerializer
from drf_spectacular.utils import extend_schema


@extend_schema(tags=['Reactions'])
class PostReactionViewSet(viewsets.ModelViewSet):
    queryset = PostReaction.objects.all()
    serializer_class = PostReactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Filter reactions by post if post_id is provided
        post_id = self.request.query_params.get('post_id')
        if post_id:
            return self.queryset.filter(post_id=post_id)
        return self.queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        return Response(self.get_serializer(instance).data)

    def destroy(self, request, *args, **kwargs):
        # Only allow deleting own reactions
        instance = self.get_object()
        if instance.user != request.user:
            return Response({'detail': 'Not authorized to delete this reaction.'}, status=403)
        
        self.perform_destroy(instance)
        return Response(status=204)