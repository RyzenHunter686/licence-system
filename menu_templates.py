from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def main_menu():
    keyboard = [
        [
            InlineKeyboardButton("🔑 Licenses", callback_data='menu_licenses'),
            InlineKeyboardButton("📈 Backtest", callback_data='menu_backtest')
        ],
        [
            InlineKeyboardButton("🤖 Bot Control", callback_data='menu_bot'),
            InlineKeyboardButton("⚙️ Settings", callback_data='menu_settings')
        ],
        [InlineKeyboardButton("📜 Logs", callback_data='view_logs')]
    ]
    return InlineKeyboardMarkup(keyboard)

def license_menu():
    keyboard = [
        [InlineKeyboardButton("📋 List All", callback_data='lic_list')],
        [InlineKeyboardButton("➕ Create New", callback_data='lic_create')],
        [InlineKeyboardButton("🔄 Reset Device", callback_data='lic_reset')],
        [InlineKeyboardButton("⏳ Extend expiry", callback_data='lic_extend')],
        [InlineKeyboardButton("⬅️ Back", callback_data='main_menu')]
    ]
    return InlineKeyboardMarkup(keyboard)

def backtest_menu():
    keyboard = [
        [InlineKeyboardButton("🚀 Run Backtest (NQ=F)", callback_data='bt_run_nq')],
        [InlineKeyboardButton("📊 Custom Symbol", callback_data='bt_custom')],
        [InlineKeyboardButton("⬅️ Back", callback_data='main_menu')]
    ]
    return InlineKeyboardMarkup(keyboard)

def bot_control_menu(status="Stopped"):
    btn_text = "🛑 Stop Bot" if status == "Running" else "🚀 Start Bot"
    btn_callback = "bot_stop" if status == "Running" else "bot_start"
    
    keyboard = [
        [InlineKeyboardButton(f"Status: {status}", callback_data='bot_status')],
        [InlineKeyboardButton(btn_text, callback_data=btn_callback)],
        [InlineKeyboardButton("🔄 Restart", callback_data='bot_restart')],
        [InlineKeyboardButton("⬅️ Back", callback_data='main_menu')]
    ]
    return InlineKeyboardMarkup(keyboard)

def settings_menu():
    keyboard = [
        [InlineKeyboardButton("📡 MongoDB URI", callback_data='set_mongo')],
        [InlineKeyboardButton("🛡️ Admin IDs", callback_data='set_admins')],
        [InlineKeyboardButton("⬅️ Back", callback_data='main_menu')]
    ]
    return InlineKeyboardMarkup(keyboard)
