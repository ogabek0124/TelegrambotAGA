import random
import json
from pathlib import Path


DATA_DIR = Path(__file__).resolve().parent.parent / "data"

def load_words():
    with open(DATA_DIR / "words.json", "r", encoding="utf-8") as f:
        return json.load(f)

words = load_words()

def generate_test():
    correct = random.choice(words)
    wrong = random.sample([w for w in words if w != correct], 3)

    options = [correct["meaning"]] + [w["meaning"] for w in wrong]
    random.shuffle(options)

    return {
        "word": correct["word"],
        "correct": correct["meaning"],
        "options": options
    }
