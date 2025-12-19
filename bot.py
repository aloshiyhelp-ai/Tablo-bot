from telegram.ext import (
    ApplicationBuilder, CommandHandler,
    MessageHandler, CallbackQueryHandler, filters
)
from config import TOKEN
from ball import on_cmd, off_cmd, show_ball, give_points, ball_callbacks

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("on", on_cmd))
app.add_handler(CommandHandler("off", off_cmd))
app.add_handler(CommandHandler("ball", show_ball))
app.add_handler(MessageHandler(filters.TEXT & filters.REPLY, give_points))
app.add_handler(CallbackQueryHandler(ball_callbacks))

print("Bot ishga tushdi...")
app.run_polling()