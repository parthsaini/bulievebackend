# users/views.py
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from .models import CustomUser, UserFinancialProfile
from .serializers import (
    UserSerializer, 
    UserCreateSerializer, 
    UserUpdateSerializer, 
    PasswordChangeSerializer,
    UserFinancialProfileSerializer
)
from .permissions import IsOwnerOrReadOnly
from drf_spectacular.utils import extend_schema


@extend_schema(tags=['Users'])
class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    permission_classes = [IsOwnerOrReadOnly]
    parser_classes = [MultiPartParser, FormParser]  # Add support for file uploads
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserSerializer

    @action(detail=False, methods=['POST'], permission_classes=[IsAuthenticated])
    def change_password(self, request):
        serializer = PasswordChangeSerializer(
            data=request.data, 
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"message": "Password changed successfully"},
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['GET'], permission_classes=[IsAuthenticated])
    def profile(self, request):
        user = request.user
        serializer = self.get_serializer(user)
        return Response(serializer.data)

    @action(detail=False, methods=['POST'], permission_classes=[IsAuthenticated], 
            parser_classes=[MultiPartParser, FormParser])
    def upload_photo(self, request):
        user = request.user
        if 'profile_photo' not in request.FILES:
            return Response(
                {"error": "No photo uploaded"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.profile_photo = request.FILES['profile_photo']
        user.save()
        
        serializer = self.get_serializer(user)
        return Response(serializer.data)




@extend_schema(tags=['User-Financial-Profile'])
class UserFinancialProfileViewSet(viewsets.ModelViewSet):
    queryset = UserFinancialProfile.objects.all()
    serializer_class = UserFinancialProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Ensure users can only access their own financial profile
        return UserFinancialProfile.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Automatically associate the profile with the current user
        serializer.save(user=self.request.user)