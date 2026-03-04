"""
Video Management Helper Script
This script helps you manage video file_ids more easily
"""

VIDEOS_TEMPLATE = """
# Copy this into your videos.py VIDEOS dictionary

VIDEOS = {
    "listening": [
        {
            "title": "📺 Listening Practice 1",
            "file_id": "PASTE_FILE_ID_HERE",
            "description": "Beginner level listening exercises",
            "duration": "5:30"
        },
        {
            "title": "📺 Listening Practice 2", 
            "file_id": "PASTE_FILE_ID_HERE",
            "description": "Intermediate listening practice",
            "duration": "8:15"
        }
    ],
    "pronunciation": [
        {
            "title": "🎤 Pronunciation Guide 1",
            "file_id": "PASTE_FILE_ID_HERE",
            "description": "Basic English pronunciation",
            "duration": "6:45"
        },
        {
            "title": "🎤 Pronunciation Guide 2",
            "file_id": "PASTE_FILE_ID_HERE",
            "description": "Advanced pronunciation",
            "duration": "7:20"
        }
    ],
    "grammar": [
        {
            "title": "✏️ Grammar Lesson 1",
            "file_id": "PASTE_FILE_ID_HERE",
            "description": "Present Simple vs Present Continuous",
            "duration": "10:00"
        },
        {
            "title": "✏️ Grammar Lesson 2",
            "file_id": "PASTE_FILE_ID_HERE",
            "description": "Past tense combinations",
            "duration": "9:30"
        }
    ],
    "vocabulary": [
        {
            "title": "📚 Vocabulary Building 1",
            "file_id": "PASTE_FILE_ID_HERE",
            "description": "Daily life vocabulary",
            "duration": "7:00"
        },
        {
            "title": "📚 Vocabulary Building 2",
            "file_id": "PASTE_FILE_ID_HERE",
            "description": "Business vocabulary",
            "duration": "8:45"
        }
    ]
}
"""


def main():
    print("=" * 70)
    print("📺 VIDEO MANAGEMENT HELPER")
    print("=" * 70)
    print()
    print("This script helps you manage video file IDs")
    print()
    print("STEPS:")
    print("1. Upload videos to your Telegram bot")
    print("2. Bot will respond with file_id for each video")
    print("3. Copy those file_ids")
    print("4. Open handlers/videos.py")
    print("5. Replace 'None' or 'PASTE_FILE_ID_HERE' with actual file_ids")
    print("6. Save and restart bot")
    print()
    print("=" * 70)
    print()
    
    choice = input("Show template? (y/n): ").lower()
    if choice == 'y':
        print(VIDEOS_TEMPLATE)
    
    print()
    print("📝 Quick Notes:")
    print("- File IDs look like: BAACAgIAAxkBAAIBEGX...")
    print("- Each video needs its own unique file_id")
    print("- Videos must be < 50MB for Telegram bots")
    print("- You can compress videos using online tools")
    print()
    
    print("💡 Testing Tips:")
    print("1. Start with just 1 video in each category")
    print("2. Test that it works before adding more")
    print("3. Check console logs for errors")
    print()
    
    print("🔗 Useful Resources:")
    print("- Video compressor: https://www.freeconvert.com/video-compressor")
    print("- Get user ID: @userinfobot on Telegram")
    print()
    print("=" * 70)


if __name__ == "__main__":
    main()
