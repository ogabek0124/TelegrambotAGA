from rest_framework import serializers
from .models import Word, Grammar, TelegramUser, Category, Video

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class WordSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = Word
        fields = ['id', 'word', 'meaning', 'level', 'category', 'category_name', 'created_at']

class GrammarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grammar
        fields = '__all__'

class TelegramUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = TelegramUser
        fields = '__all__'

class VideoSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = Video
        fields = ['id', 'title', 'description', 'level', 'youtube_url', 'thumbnail', 
                  'duration_seconds', 'category', 'category_name', 'views', 'created_at']
