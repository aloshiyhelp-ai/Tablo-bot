from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import database as db

async def callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    chat_id = str(query.message.chat.id)

    if query.data == "top_all":
        # Umumiy reyting
        cursor = db.conn.cursor()
        cursor.execute("""
            SELECT target_name, SUM(points) as total_points 
            FROM points 
            WHERE chat_id=? 
            GROUP BY target_id 
            ORDER BY total_points DESC 
            LIMIT 10
        """, (chat_id,))
        rows = cursor.fetchall()

        if not rows:
            await query.edit_message_text("Hali hech kim ball to‘plamagan.")
            return

        text = "📊 *Guruhdagi umumiy reyting:*\n\n"
        medals = ["🥇", "🥈", "🥉"]
        for i, (name, pts) in enumerate(rows, 1):
            medal = medals[i-1] if i <= 3 else "🎗"
            text += f"{i}. {medal} {name} ➖ {pts} ball\n"

        await query.edit_message_text(text, parse_mode="Markdown")

    elif query.data == "topics_list":
        # Mavzular ro'yxati
        topics = db.get_all_topics(chat_id)
        if not topics:
            await query.edit_message_text("Hozircha mavzular mavjud emas.")
            return

        buttons = [[InlineKeyboardButton(t, callback_data=f"topic_{t}")] for t in topics]
        keyboard = InlineKeyboardMarkup(buttons)
        await query.edit_message_text("📚 Mavzular:", reply_markup=keyboard)

    elif query.data.startswith("topic_"):
        topic_name = query.data[6:]  # "topic_" ni olib tashlaymiz
        top = db.get_topic_top(chat_id, topic_name, limit=10)
        if not top:
            await query.edit_message_text(f"📚 *'{topic_name}' mavzusi natijalari:* \nHali ball yo‘q.", parse_mode="Markdown")
            return

        text = f"📚 *'{topic_name}' mavzusi natijalari:*\n"
        medals = ["🥇", "🥈", "🥉"]
        for i, (name, pts) in enumerate(top, 1):
            medal = medals[i-1] if i <=3 else "🎗"
            text += f"{i}. {medal} {name} ➖ {pts} ball\n"

        await query.edit_message_text(text, parse_mode="Markdown")