from django.shortcuts import render
from rest_framework import viewsets, filters
from .models import Word, Grammar, TelegramUser, Category, Video
from .serializers import WordSerializer, GrammarSerializer, TelegramUserSerializer, CategorySerializer, VideoSerializer

def home_view(request):
    stats = {
        'words_count': Word.objects.count(),
        'grammar_count': Grammar.objects.count(),
        'users_count': TelegramUser.objects.count(),
        'videos_count': Video.objects.count(),
    }
    recent_words = Word.objects.all().order_by('-created_at')[:5]
    top_users = TelegramUser.objects.all().order_by('-streak')[:5]
    
    return render(request, 'home.html', {
        'stats': stats,
        'recent_words': recent_words,
        'top_users': top_users,
    })

class WordViewSet(viewsets.ModelViewSet):
    queryset = Word.objects.all()
    serializer_class = WordSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['word', 'meaning']

    def get_queryset(self):
        level = self.request.query_params.get('level')
        if level:
            return self.queryset.filter(level=level)
        return self.queryset

class GrammarViewSet(viewsets.ModelViewSet):
    queryset = Grammar.objects.all()
    serializer_class = GrammarSerializer

class TelegramUserViewSet(viewsets.ModelViewSet):
    queryset = TelegramUser.objects.all()
    serializer_class = TelegramUserSerializer
    lookup_field = 'telegram_id'

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class VideoViewSet(viewsets.ModelViewSet):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'description']
    
    def get_queryset(self):
        level = self.request.query_params.get('level')
        category = self.request.query_params.get('category')
        queryset = self.queryset
        
        if level:
            queryset = queryset.filter(level=level)
        if category:
            queryset = queryset.filter(category__id=category)
        
        return queryset
