from rest_framework import serializers
from .models import Word, Grammar, TelegramUser, Category

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
