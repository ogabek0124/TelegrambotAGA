from django.contrib import admin
from .models import Word, Grammar, TelegramUser, Category, Video

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(Word)
class WordAdmin(admin.ModelAdmin):
    list_display = ['word', 'level', 'category', 'created_at']
    list_filter = ['level', 'category']
    search_fields = ['word', 'meaning']

@admin.register(Grammar)
class GrammarAdmin(admin.ModelAdmin):
    list_display = ['title', 'level', 'created_at']
    list_filter = ['level']
    search_fields = ['title', 'explanation']

@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = ['telegram_id', 'first_name', 'username', 'level', 'streak', 'created_at']
    list_filter = ['level', 'created_at']
    search_fields = ['telegram_id', 'first_name', 'username']
    readonly_fields = ['telegram_id', 'created_at', 'updated_at']

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ['title', 'level', 'category', 'duration_seconds', 'views', 'created_at']
    list_filter = ['level', 'category', 'created_at']
    search_fields = ['title', 'description']
    readonly_fields = ['views', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('title', 'description', 'level', 'category')
        }),
        ('Video Source', {
            'fields': ('youtube_url', 'thumbnail')
        }),
        ('Metadata', {
            'fields': ('duration_seconds', 'views', 'created_at', 'updated_at')
        }),
    )

