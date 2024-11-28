from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PostReactionViewSet

router = DefaultRouter()
router.register(r'reactions', PostReactionViewSet)

urlpatterns = [
    path('', include(router.urls)),
]