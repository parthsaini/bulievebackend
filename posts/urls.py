from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CommunityViewSet, PostViewSet, CommentViewSet, CommunityMemberViewSet

router = DefaultRouter()
router.register(r'communities', CommunityViewSet)
router.register(r'posts', PostViewSet, basename='posts')
router.register(r'comments', CommentViewSet)
router.register(r'community-members', CommunityMemberViewSet)

urlpatterns = [
    path('', include(router.urls)),
]