import random
import json

def load_words():
    with open("data/words.json", "r", encoding="utf-8") as f:
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
