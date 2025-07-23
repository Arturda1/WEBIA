import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, ContextTypes
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.environ.get("TG_BOT_TOKEN")
ADMIN_CHAT_ID = os.environ.get("TG_ADMIN_CHAT_ID")

app = Application.builder().token(BOT_TOKEN).build()

# Функция отправки запроса на подтверждение
async def send_confirmation(op_id, message_text):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Подтвердить", callback_data=f"confirm:{op_id}"),
         InlineKeyboardButton("❌ Отменить", callback_data=f"cancel:{op_id}")]
    ])
    await app.bot.send_message(chat_id=ADMIN_CHAT_ID, text=message_text, reply_markup=keyboard)

# Обработка кнопок
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text=f"Вы выбрали: {query.data}")

# Запуск бота (для telegram_runner.py)
async def start_bot():
    app.add_handler(CallbackQueryHandler(handle_callback))
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
