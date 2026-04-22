import os
import logging
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from license_manager import LicenseManager, IST
from menu_templates import main_menu, license_list_menu, license_detail_menu, confirmation_menu
from dotenv import load_dotenv

# Load Environment Variables
load_dotenv()

# Logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Config
TOKEN = os.getenv("TELEGRAM_TOKEN")
MONGO_URI = os.getenv("MONGO_URI")
ADMIN_ID = 8301986273

WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# Initialize Managers
lic_manager = LicenseManager(MONGO_URI)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    await update.message.reply_text(
        "🎯 **HUNTER BOT: ADVANCED PANEL**\n"
        "Manage your licensing system with ease below.",
        reply_markup=main_menu(),
        parse_mode='Markdown'
    )

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data.split(':')
    prefix = data[0]
    action = data[1] if len(data) > 1 else None
    
    # NAVIGATION
    if prefix == 'menu':
        if action == 'main':
            await query.edit_message_text("🎯 **HUNTER BOT: ADVANCED PANEL**", reply_markup=main_menu(), parse_mode='Markdown')
            
    # BROWSE FLOW
    elif prefix == 'lic':
        if action == 'browse':
            page = int(data[2]) if len(data) > 2 else 0
            licenses = lic_manager.list_licenses(limit=10, skip=page*10)
            await query.edit_message_text("📋 **Select a license to view details:**", reply_markup=license_list_menu(licenses, page), parse_mode='Markdown')
            
        elif action == 'view':
            key = data[2]
            lic = lic_manager.get_license(key)
            if not lic:
                await query.edit_message_text("❌ License not found.", reply_markup=main_menu())
                return
                
            status = lic.get('status', 'active').upper()
            expires = lic.get('expires_at').strftime('%Y-%m-%d %H:%M') if lic.get('expires_at') else "Never"
            details = (
                f"🔑 **License Details**\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"👤 Nickname: `{lic.get('nickname', 'N/A')}`\n"
                f"🗝️ Key: `{lic.get('key')}`\n"
                f"📅 Expiry: `{expires}`\n"
                f"🛡️ Status: **{status}**\n"
                f"💻 Device: `{lic.get('device_id') or 'Not Linked'}`\n"
                f"━━━━━━━━━━━━━━━━━━━━"
            )
            await query.edit_message_text(details, reply_markup=license_detail_menu(key), parse_mode='Markdown')
            
        elif action == 'create':
             await query.edit_message_text("➕ **Create New License**\n\nUse: `/create nickname days`", reply_markup=main_menu(), parse_mode='Markdown')

        # ACTIONS
        elif action == 'rst':
            key = data[2]
            lic_manager.reset_device(key)
            await query.edit_message_text(f"✅ Device Reset for `{key}`", reply_markup=license_detail_menu(key), parse_mode='Markdown')

        elif action == 'stt':
            key = data[2]
            lic = lic_manager.get_license(key)
            new_st = 'revoked' if lic.get('status') == 'active' else 'active'
            lic_manager.update_status(key, new_st)
            await handle_callback(update, context) # Refresh view

        elif action == 'ext_ui':
            key = data[2]
            await query.edit_message_text(f"⏳ **Extend Key: `{key}`**\n\nUse: `/extend {key} 30`", reply_markup=license_detail_menu(key), parse_mode='Markdown')

        elif action == 'del_ui':
            key = data[2]
            await query.edit_message_text(f"❌ **ARE YOU SURE?**\n\nDeleting `{key}` is permanent.", reply_markup=confirmation_menu('del', key), parse_mode='Markdown')

        elif action == 'del':
            key = data[2]
            lic_manager.delete_license(key)
            await query.edit_message_text(f"🗑️ Key `{key}` deleted permanently.", reply_markup=main_menu(), parse_mode='Markdown')

# Command Handlers (Fallback for quick use)
async def create_lic_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    if not context.args or len(context.args) < 2:
        await update.message.reply_text("❌ Usage: `/create nickname days`", parse_mode='Markdown')
        return
    nickname, days = context.args[0], int(context.args[1])
    res = lic_manager.create_license(nickname, days)
    await update.message.reply_text(f"✅ Created: `{res['key']}`\nUser: `{res['nickname']}`", parse_mode='Markdown')

async def extend_lic_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    if not context.args or len(context.args) < 2:
        await update.message.reply_text("❌ Usage: `/extend KEY DAYS`", parse_mode='Markdown')
        return
    key, days = context.args[0], int(context.args[1])
    if lic_manager.extend_license(key, days):
        await update.message.reply_text(f"✅ Extended `{key}` by {days} days.", parse_mode='Markdown')
    else:
        await update.message.reply_text("❌ Key not found.")

# FastAPI App
app = FastAPI()
tg_app = ApplicationBuilder().token(TOKEN).build()

tg_app.add_handler(CommandHandler("start", start))
tg_app.add_handler(CommandHandler("create", create_lic_cmd))
tg_app.add_handler(CommandHandler("extend", extend_lic_cmd))
tg_app.add_handler(CallbackQueryHandler(handle_callback))

@app.on_event("startup")
async def startup():
    await tg_app.initialize()
    await tg_app.start()
    if WEBHOOK_URL:
        try:
            await tg_app.bot.set_webhook(f"{WEBHOOK_URL.rstrip('/')}/webhook")
            logger.info("Webhook set.")
        except Exception as e:
            logger.error(f"Webhook error: {e}")

@app.post("/webhook")
async def webhook(request: Request):
    try:
        data = await request.json()
        await tg_app.process_update(Update.de_json(data, tg_app.bot))
    except Exception as e: logger.error(f"Update error: {e}")
    return {"status": "ok"}

@app.get("/")
@app.head("/")
async def health(): return {"status": "online"}
