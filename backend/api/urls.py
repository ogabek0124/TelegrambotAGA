from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WordViewSet, GrammarViewSet, TelegramUserViewSet, CategoryViewSet

router = DefaultRouter()
router.register(r'words', WordViewSet)
router.register(r'grammar', GrammarViewSet)
router.register(r'users', TelegramUserViewSet)
router.register(r'categories', CategoryViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
