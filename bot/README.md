# InglizchaOson Bot 🚀

**Professional English Learning Telegram Bot**

---

## 📚 Features

### 🎓 Level System
- **Beginner** - Yangi boshlanuvchilar
- **Intermediate** - O'rta daraja
- **IELTS** - Yuqori daraja

### 📘 So'zlar (Vocabulary)
- Level'ga mos so'zlar
- 18+ ta professional so'z
- Beginner dan IELTS gacha

### 📚 Grammar
- 10+ ta grammar mavzu
- Level'ga mos darslari
- Qoida, misol, tushuntirish bilan

### 📝 Test System
- Multiple choice questions (A/B/C/D)
- Level'ga mos testlar
- Natija saqlanadi
- Progress kuzatiladi

### 📌 Daily Lesson
- Har kun 1 ta so'z
- Har kun 1 ta grammar
- Bugun o'qilganmi tekshirish

### 🔥 Streak System
- Kunlik streak kuzatish
- Badge va achievement:
  - 🆕 Beginner
  - 🌟 Rising (3+ kun)
  - 🔥 Hot (7+ kun)
  - ⭐ Master (14+ kun)
  - 🏅 Champion (21+ kun)
  - 💎 Legend (30+ kun)

### 📊 Progress Tracking
- Test statistikasi
- Foiz hisoblash
- Streak kuzatish
- Level'ni ko'rsatish

### 🏆 Leaderboard
- Top 10 foydalanuvchilar
- Streak bo'yicha reyting
- So'z soni bo'yicha

---

## 🛠️ Tech Stack

- **Language**: Python 3.10
- **Bot Framework**: aiogram 3.x
- **Database**: SQLite
- **Platform**: Telegram

---

## 📦 Installation

```bash
# 1. Clone repository
git clone https://github.com/yourusername/inglizchaoson_bot.git
cd inglizchaoson_bot

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

# 4. Install requirements
pip install aiogram

# 5. Set TOKEN in config.py
# Add your bot token from BotFather

# 6. Run bot
python bot.py
```

---

## 📂 Project Structure

```
inglizchaoson_bot/
├── bot.py              # Main bot file
├── config.py           # Bot configuration
├── handlers/           # Message handlers
│   ├── start.py
│   ├── level.py
│   ├── words.py
│   ├── test.py
│   ├── grammar.py
│   ├── progress.py
│   ├── leaderboard.py
│   ├── daily.py
│   └── streak.py
├── keyboards/          # Keyboard layouts
│   ├── menus.py
│   ├── level_menu.py
│   ├── grammar_menu.py
│   └── test_keyboard.py
├── services/           # Database & utilities
│   └── db.py
├── data/               # Data files
│   ├── words.json
│   ├── grammar.json
│   └── progress.db
└── README.md           # This file
```

---

## 🎯 How to Use

1. **/start** - Botni ishga tushirish
2. **🎓 Drajani tanlash** - Level tanlash
3. **📘 So'zlar** - Level so'zlarini ko'rish
4. **📝 Test** - Test yechish
5. **📚 Grammar** - Grammar mavzuları
6. **📌 Bugun darsga** - Daily lesson
7. **🔥 Streakga** - Streak va badge ko'rish
8. **📊 Progress** - Statistika
9. **🏆 Leaderboard** - Reyting

---

## 📈 3-Week Development Plan

### Week 1 ✅
- Foundation setup
- Menu system
- SQLite database
- Test implementation
- Progress tracking

### Week 2 ✅
- Level system
- Grammar engine
- Level-based tests
- Words by level
- UX improvements

### Week 3 ✅
- Daily lessons
- Streak system
- Badge achievements
- Progress upgrade
- Final polish

---

## 🔮 Future Features

- 🎧 Audio pronunciation
- 📸 Images for words
- 🤖 AI tutoring
- 📱 Mobile app
- 🌍 Multi-language support

---

## 👨‍💻 Author

**Your Name**
- GitHub: [@yourusername](https://github.com/yourusername)
- Telegram: [@yourusername](https://t.me/yourusername)

---

## 📝 License

MIT License - Feel free to use this project!

---

## 🤝 Contributing

Pull requests are welcome!

---

## 📞 Support

Savollar bo'lsa:
- Telegram: [@yourusername](https://t.me/yourusername)
- Email: your.email@example.com

---

**Made with ❤️ for English learners**
