import os
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo

MINI_APP_URL = os.getenv("MINI_APP_URL", "")


def main_menu() -> ReplyKeyboardMarkup:
    row2 = [KeyboardButton(text="📅 Мої записи"), KeyboardButton(text="⚙️ Налаштування")]
    if MINI_APP_URL:
        row2.append(KeyboardButton(text="🗂 Журнал", web_app=WebAppInfo(url=MINI_APP_URL)))
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🌙 Сон"), KeyboardButton(text="💡 Ідея")],
            row2,
        ],
        resize_keyboard=True,
        input_field_placeholder="Надішли голосове або текст...",
    )


def entry_type_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🌙 Сон", callback_data="type:dream"),
            InlineKeyboardButton(text="💡 Ідея", callback_data="type:idea"),
            InlineKeyboardButton(text="💭 Думка", callback_data="type:thought"),
        ]
    ])


def settings_keyboard(notifications_enabled: bool) -> InlineKeyboardMarkup:
    notif_text = "🔔 Вимкнути нагадування" if notifications_enabled else "🔕 Увімкнути нагадування"
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=notif_text, callback_data="settings:toggle_notifications")],
        [InlineKeyboardButton(text="🕐 Час нагадування", callback_data="settings:set_time")],
        [InlineKeyboardButton(text="🌐 Мова", callback_data="settings:language")],
    ])


def history_keyboard(entries: list[dict]) -> InlineKeyboardMarkup:
    """Show last 5 entries as inline buttons."""
    buttons = []
    type_emoji = {"dream": "🌙", "idea": "💡", "thought": "💭"}
    for entry in entries[:5]:
        emoji = type_emoji.get(entry["type"], "📝")
        date = entry["created_at"][:10]
        text = entry["raw_text"][:30] + "..." if len(entry["raw_text"]) > 30 else entry["raw_text"]
        buttons.append([
            InlineKeyboardButton(
                text=f"{emoji} {date} — {text}",
                callback_data=f"entry:{entry['id']}"
            )
        ])
    return InlineKeyboardMarkup(inline_keyboard=buttons) if buttons else None
