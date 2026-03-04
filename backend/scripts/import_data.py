import os
import sys
import json
import sqlite3
import django
from datetime import date

# Set up Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from api.models import Word, Grammar, TelegramUser, Category

def import_words():
    words_file = '../bot/data/words.json'
    if os.path.exists(words_file):
        with open(words_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for item in data:
                Word.objects.get_or_create(
                    word=item['word'],
                    meaning=item['meaning'],
                    level=item['level']
                )
        print(f"Imported {len(data)} words.")

def import_grammar():
    grammar_file = '../bot/data/grammar.json'
    if os.path.exists(grammar_file):
        with open(grammar_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for item in data:
                Grammar.objects.get_or_create(
                    title=item['title'],
                    level=item['level'],
                    rule=item['rule'],
                    example=item['example'],
                    explanation=item['explanation']
                )
        print(f"Imported {len(data)} grammar lessons.")

def import_users():
    db_file = '../bot/data/progress.db'
    if os.path.exists(db_file):
        conn = sqlite3.connect(db_file)
        c = conn.cursor()
        c.execute("SELECT user_id, correct, total, streak, last_date, level FROM progress")
        rows = c.fetchall()
        for row in rows:
            user_id, correct, total, streak, last_date, level = row
            # Convert last_date to date object if exists
            l_date = None
            if last_date:
                try:
                    l_date = date.fromisoformat(last_date)
                except:
                    pass
            
            TelegramUser.objects.update_or_create(
                telegram_id=user_id,
                defaults={
                    'correct': correct,
                    'total': total,
                    'streak': streak,
                    'last_date': l_date,
                    'level': level or 'beginner'
                }
            )
        print(f"Imported {len(rows)} users.")
        conn.close()

if __name__ == '__main__':
    print("Starting import...")
    import_words()
    import_grammar()
    import_users()
    print("Import finished.")
