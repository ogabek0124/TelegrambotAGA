"""Business logic helpers.

Keeping reusable non-handler logic in one place helps handlers stay light.
"""

from services.db import get_admin_stats, get_referral_stats


def format_stats_message() -> str:
    stats = get_admin_stats()
    return (
        "📊 <b>Bot statistikasi</b>\n\n"
        f"👥 Jami foydalanuvchilar: <b>{stats['total_users']}</b>\n"
        f"📈 Bugun qo'shilgan: <b>{stats['today_joined']}</b>\n"
        f"⚡ Aktiv foydalanuvchilar: <b>{stats['active_users']}</b>"
    )


def format_referral_message(user_id: int, link: str) -> str:
    data = get_referral_stats(user_id)
    return (
        "🔗 <b>Sizning referral linkingiz</b>\n\n"
        f"{link}\n\n"
        "Do'stlaringiz shu link orqali kirsa sizga bonus yoziladi.\n\n"
        f"👥 Taklif qilganlar: <b>{data['referral_count']}</b>\n"
        f"🎁 Bonus: <b>{data['bonus']}</b>"
    )
