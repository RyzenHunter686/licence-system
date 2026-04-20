import os
import logging
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from license_manager import LicenseManager, IST
from menu_templates import main_menu, license_menu

# Logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Config
TOKEN = os.getenv("TELEGRAM_TOKEN")
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://ryzen_hunter:Ryzhunteryt098%24%40@hunterbot.beaj4bf.mongodb.net/hunter_bot?retryWrites=true&w=majority&appName=hunterbot")
ADMIN_ID = 8301986273

WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# Initialize Managers
lic_manager = LicenseManager(MONGO_URI)

# Bot Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text("🚫 Unauthorized access.")
        return
    await update.message.reply_text(
        "🎯 **HUNTER BOT: ADMIN PANEL**\n"
        "Welcome! Use the menu below to manage your licenses.",
        reply_markup=main_menu(),
        parse_mode='Markdown'
    )

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == 'main_menu':
        await query.edit_message_text("🎯 **HUNTER BOT: ADMIN PANEL**", reply_markup=main_menu(), parse_mode='Markdown')
        
    elif query.data == 'lic_list':
        licenses = lic_manager.list_licenses(limit=10)
        if not licenses:
            text = "❌ No licenses found."
        else:
            text = "📋 **Active Licenses**\n\n"
            for lic in licenses:
                status = lic.get('status', 'active').upper()
                key = lic.get('key')
                user = lic.get('nickname', 'N/A')
                text += f"• `{key}` | **{user}** ({status})\n"
        
        await query.edit_message_text(text, reply_markup=main_menu(), parse_mode='Markdown')

    elif query.data == 'lic_create':
        await query.edit_message_text(
            "➕ **Create New Key**\n\n"
            "Use: `/create nickname days`\n"
            "Example: `/create JohnVip 30`",
            reply_markup=main_menu(),
            parse_mode='Markdown'
        )

    elif query.data == 'lic_reset':
        await query.edit_message_text(
            "🔄 **Reset Device ID**\n\n"
            "Use: `/reset KEY`\n"
            "Example: `/reset HT-ABCD-EFGH`",
            reply_markup=main_menu(),
            parse_mode='Markdown'
        )


async def create_lic_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    if not context.args or len(context.args) < 2:
        await update.message.reply_text("❌ Usage: `/create nickname days`", parse_mode='Markdown')
        return
    
    nickname = context.args[0]
    try:
        days = int(context.args[1])
        res = lic_manager.create_license(nickname, days)
        await update.message.reply_text(
            f"✅ **License Created**\n\n"
            f"👤 User: `{res['nickname']}`\n"
            f"🔑 Key: `{res['key']}`\n"
            f"⏳ Expires: `{res['expires_at'].strftime('%Y-%m-%d %H:%M IST')}`",
            parse_mode='Markdown'
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

async def reset_lic_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    if not context.args:
        await update.message.reply_text("❌ Usage: `/reset KEY`", parse_mode='Markdown')
        return
    
    key = context.args[0]
    if lic_manager.reset_device(key):
        await update.message.reply_text(f"✅ Device reset successful for `{key}`", parse_mode='Markdown')
    else:
        await update.message.reply_text(f"❌ License not found or already reset.")

# FastAPI App
app = FastAPI()
tg_app = ApplicationBuilder().token(TOKEN).build()

# Register Handlers
tg_app.add_handler(CommandHandler("start", start))
tg_app.add_handler(CommandHandler("create", create_lic_cmd))
tg_app.add_handler(CommandHandler("reset", reset_lic_cmd))
tg_app.add_handler(CallbackQueryHandler(handle_callback))


@app.on_event("startup")
async def startup():
    await tg_app.initialize()
    await tg_app.start()  # Start the application logic
    if WEBHOOK_URL:
        # Ensure URL is clean and starts with https
        clean_url = WEBHOOK_URL.rstrip('/')
        if not clean_url.startswith('https://'):
            logger.warning("WEBHOOK_URL should start with https://")
        
        await tg_app.bot.set_webhook(f"{clean_url}/webhook")
        logger.info(f"Webhook set to {clean_url}/webhook")

@app.on_event("shutdown")
async def shutdown():
    await tg_app.stop()
    await tg_app.shutdown()

@app.post("/webhook")
async def webhook(request: Request):
    try:
        data = await request.json()
        update = Update.de_json(data, tg_app.bot)
        await tg_app.process_update(update)
    except Exception as e:
        logger.error(f"Error processing update: {e}")
    return {"status": "ok"}

@app.get("/")
@app.head("/")
async def health():
    return {"status": "online", "bot": "Hunter Bot License Manager"}


@app.get("/health")
async def health_check():
    return {"status": "ok"}
