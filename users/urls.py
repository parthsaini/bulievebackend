# users/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, UserFinancialProfileViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'financial-profiles', UserFinancialProfileViewSet, basename='financial-profile')

urlpatterns = [
    path('', include(router.urls)),
    # Optional: Add JWT token endpoints if using Simple JWT
    # path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]