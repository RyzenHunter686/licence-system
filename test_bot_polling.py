import os
import logging
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from license_manager import LicenseManager
from menu_templates import main_menu


# Logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# CONFIGURATION - EDIT THESE
TOKEN = "8724140547:AAFVEY76fCq5DkwA43qC7pxi-qiXSfFWgR0"
MONGO_URI = "mongodb+srv://ryzen_hunter:Ryzhunteryt098%24%40@hunterbot.beaj4bf.mongodb.net/hunter_bot?retryWrites=true&w=majority&appName=hunterbot"
ADMIN_ID = 8301986273 # <--- I WILL SET THIS FOR YOU

# Initialize Managers
lic_manager = LicenseManager(MONGO_URI)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    logger.info(f"Received /start from user: {user_id}")
    if user_id != ADMIN_ID:
        await update.message.reply_text(f"🚫 Unauthorized. Your ID is: {user_id}")
        return
    await update.message.reply_text(
        "🎯 **LOCAL TEST: ADMIN PANEL**\n"
        "Welcome! If you see this, the bot is working locally.",
        reply_markup=main_menu(),
        parse_mode='Markdown'
    )

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == 'main_menu':
        await query.edit_message_text("🎯 **LOCAL TEST: ADMIN PANEL**", reply_markup=main_menu(), parse_mode='Markdown')
        
    elif query.data == 'lic_list':
        await query.edit_message_text("📋 **Listing Licenses...** (DB connected)", reply_markup=main_menu(), parse_mode='Markdown')

    elif query.data == 'lic_create':
        await query.edit_message_text("➕ **Create Key Mode**\nUse: `/create nickname days`", reply_markup=main_menu(), parse_mode='Markdown')


def run_test():
    print("Starting Bot in POLLING mode...")
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.run_polling()

if __name__ == "__main__":
    run_test()

