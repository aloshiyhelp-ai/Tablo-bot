from telegram import InlineKeyboardButton, InlineKeyboardMarkup

async def help_cmd(message):
    buttons = [
        InlineKeyboardButton("👤 Profilim", callback_data="profile"),
        InlineKeyboardButton("🌐 Til", callback_data="lang"),
        InlineKeyboardButton("⚙️ Sozlamalar", callback_data="settings"),
        InlineKeyboardButton("👥 Guruhlarim", callback_data="groups"),
        InlineKeyboardButton("ℹ️ Admin haqida", callback_data="about"),
        InlineKeyboardButton("🛠 Admin panel", callback_data="admin"),
    ]
    keyboard = [buttons[i:i+3] for i in range(0, len(buttons), 3)]
    await message.reply_text(
        "📘 *Qo‘llanma*\n\n"
        "Reply + `✅` → +5 ball\n"
        "/ball → guruh reytingi\n"
        "/myball → mening ballarim",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )