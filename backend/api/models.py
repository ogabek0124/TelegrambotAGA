from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name

class Word(models.Model):
    LEVEL_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('ielts', 'IELTS'),
    ]
    word = models.CharField(max_length=100)
    meaning = models.CharField(max_length=200)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='beginner')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.word} ({self.level})"

class Grammar(models.Model):
    LEVEL_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('ielts', 'IELTS'),
    ]
    title = models.CharField(max_length=200)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='beginner')
    rule = models.TextField()
    example = models.TextField()
    explanation = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class TelegramUser(models.Model):
    telegram_id = models.BigIntegerField(unique=True)
    username = models.CharField(max_length=100, null=True, blank=True)
    first_name = models.CharField(max_length=100, null=True, blank=True)
    
    # Progress fields
    correct = models.IntegerField(default=0)
    total = models.IntegerField(default=0)
    streak = models.IntegerField(default=0)
    last_date = models.DateField(null=True, blank=True)
    level = models.CharField(max_length=20, default='beginner')
    
    # Dates
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"User {self.telegram_id} - {self.username or self.first_name}"


class Video(models.Model):
    LEVEL_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('ielts', 'IELTS'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='beginner')
    
    # Video source (YouTube URL, file upload, etc.)
    youtube_url = models.URLField(null=True, blank=True)
    thumbnail = models.ImageField(upload_to='thumbnails/', null=True, blank=True)
    
    # Duration
    duration_seconds = models.IntegerField(null=True, blank=True)
    
    # Metadata
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    views = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title} ({self.level})"
    
    class Meta:
        ordering = ['-created_at']
