import os
from dotenv import load_dotenv

load_dotenv()

def _clean_env(value: str | None) -> str:
	if not value:
		return ""
	cleaned = value.strip().strip('"').strip("'")
	# Render'da ba'zan xato bilan "BOT_TOKEN=..." ko'rinishida value kiritiladi.
	if cleaned.startswith("BOT_TOKEN="):
		cleaned = cleaned.split("=", 1)[1].strip()
	return cleaned


TOKEN = _clean_env(os.getenv("BOT_TOKEN") or os.getenv("TOKEN"))
if not TOKEN:
	raise RuntimeError("BOT_TOKEN topilmadi. Render Environment Variables ga to'g'ri token kiriting.")

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///data/progress.db")
DEBUG = os.getenv("DEBUG", "False") == "True"
BOT_USERNAME = _clean_env(os.getenv("BOT_USERNAME"))
REDIS_URL = _clean_env(os.getenv("REDIS_URL"))


def _parse_admin_ids(value: str | None) -> set[int]:
	if not value:
		return set()
	result = set()
	for part in value.split(","):
		part = part.strip()
		if part.isdigit():
			result.add(int(part))
	return result


ADMIN_IDS = _parse_admin_ids(os.getenv("ADMIN_IDS"))

