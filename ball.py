import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import database as db
from utils import is_admin

# ================= /on =================
async def on_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        await update.message.reply_text("❌ Siz admin emassiz")
        return

    if not context.args:
        await update.message.reply_text("⚠️ Mavzu nomini yozing: /on Mavzu")
        return

    chat_id = str(update.effective_chat.id)
    user = update.effective_user
    topic = " ".join(context.args)

    db.start_session(chat_id, str(user.id), user.full_name, topic)
    await update.message.reply_text(
        f"✅ '{topic}' mavzusi boshlandi!\n👑 Boshlovchi: {user.full_name}"
    )

# ================= /off =================
async def off_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        await update.message.reply_text("❌ Siz admin emassiz")
        return

    chat_id = str(update.effective_chat.id)
    session = db.get_session(chat_id)
    if not session:
        await update.message.reply_text("⚠️ Faol mavzu yo‘q")
        return

    topic = session["topic_name"]
    starter = session["starter_name"]
    top = db.get_topic_top(chat_id, topic)

    # 1️⃣ NATIJALAR
    text = f"📚 *{topic}* mavzusi yakunlandi 🏁\n\n🏆 *Yakuniy natijalar:*\n"
    medals = ["🥇", "🥈", "🥉"]

    for i, (name, pts) in enumerate(top, 1):
        medal = medals[i-1] if i <= 3 else "🎗"
        text += f"{i}. {medal} {name} ➖ {pts} ball\n"

    await update.message.reply_text(text, parse_mode="Markdown")

    # 2️⃣ G‘OLIBNI TABRIKLASH
    if top:
        winner_name, winner_pts = top[0]
        await update.message.reply_text(
            f"🎉 Tabriklaymiz, *{winner_name}*!\n"
            f"🏆 Siz {winner_pts} ball bilan g‘olib bo‘ldingiz!",
            parse_mode="Markdown"
        )

    # 3️⃣ BOSHLOVCHIGA RAHMAT
    await update.message.reply_text(
        f"🙏 Hurmatli *{starter}*,\n"
        f"mavzuni olib borganingiz uchun tashakkur!",
        parse_mode="Markdown"
    )

    db.stop_session(chat_id)

# ================= BALL BERISH =================
async def give_points(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not msg or msg.text.strip() != "✅" or not msg.reply_to_message:
        return

    chat_id = str(update.effective_chat.id)
    session = db.get_session(chat_id)
    if not session:
        return

    if str(update.effective_user.id) != session["starter_id"]:
        await msg.reply_text(
            f"❌ Siz boshlovchi emassiz\n👑 Boshlovchi: {session['starter_name']}"
        )
        return

    replied = msg.reply_to_message
    if not replied.from_user or replied.from_user.is_bot:
        await msg.reply_text("❌ Ball faqat foydalanuvchiga beriladi")
        return

    target_id = f"user_{replied.from_user.id}"
    target_name = replied.from_user.full_name
    topic = session["topic_name"]

    db.add_topic_points(chat_id, topic, target_id, target_name, 5)
    db.add_points(chat_id, target_id, target_name, 5)

    await msg.reply_text(f"✅ +5 ball\n👤 {target_name}\n📚 {topic}")
    await asyncio.sleep(0.1)

# ================= MENU =================
# ================= MENU (ichki) =================
def ball_menu():
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("🎯 Ballarim", callback_data="my_total"),
        InlineKeyboardButton("📊 Reyting", callback_data="top_all"),
        InlineKeyboardButton("📚 Mavzular", callback_data="topics_list")
    ]])

# ================= /ball =================
async def show_ball(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📊 Tanlang:", reply_markup=ball_menu())

# ================= CALLBACK =================
async def ball_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    uid = f"user_{q.from_user.id}"

    # 🔙 BACK TUGMALAR
    back_main = InlineKeyboardMarkup([
        [InlineKeyboardButton("⬅️ Ortga", callback_data="back_main")]
    ])
    back_topics = InlineKeyboardMarkup([
        [InlineKeyboardButton("⬅️ Ortga", callback_data="back_topics")]
    ])

    # 🔙 ASOSIY MENYU
    if q.data == "back_main":
        await q.edit_message_text("📊 Tanlang:", reply_markup=ball_menu())
        return

    # 🔙 MAVZULAR RO‘YXATI
    if q.data in ["back_topics", "topics_list"]:
        chat_id = str(q.message.chat.id)
        topics = db.get_all_topics(chat_id)

        if not topics:
            await q.edit_message_text("Hozircha mavzular mavjud emas.")
            return

        # Tugmalarni 3 tadan bir qatorga joylash
        kb = []
        row = []
        for i, t in enumerate(topics, 1):
            row.append(InlineKeyboardButton(t, callback_data=f"topic_{t}"))
            if i % 3 == 0:
                kb.append(row)
                row = []
        if row:
            kb.append(row)

        # Ortga tugma alohida qatorda
        kb.append([InlineKeyboardButton("⬅️ Ortga", callback_data="back_main")])

        await q.edit_message_text(
            "📚 Mavzular:",
            reply_markup=InlineKeyboardMarkup(kb)
        )
        return

    # 🎯 BALLARIM
    if q.data == "my_total":
        total = db.get_user_total(uid)
        topics = db.get_user_topics(uid)

        text = f"📊 *Sizning ballaringiz:*\n🪙 Umumiy: {total} ball\n\n"
        for t, p in topics:
            text += f"🏷 {t} — {p} ball\n"

        await q.edit_message_text(text, parse_mode="Markdown", reply_markup=back_main)
        return

    # 📊 REYTING
    elif q.data == "top_all":
        top = db.get_overall_top()
        text = "📊 *Umumiy reyting:*\n\n"
        for i, (n, p) in enumerate(top, 1):
            text += f"{i}. {n} ➖ {p} ball\n"

        await q.edit_message_text(text, parse_mode="Markdown", reply_markup=back_main)
        return

    # 📌 BITTA MAVZU
    elif q.data.startswith("topic_"):
        chat_id = str(q.message.chat.id)
        topic = q.data.replace("topic_", "")
        top = db.get_topic_top(chat_id, topic)

        text = f"📚 *'{topic}' natijalari:*\n"
        for i, (n, p) in enumerate(top, 1):
            text += f"{i}. {n} ➖ {p} ball\n"

        await q.edit_message_text(text, parse_mode="Markdown", reply_markup=back_topics)
        return