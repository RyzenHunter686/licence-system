from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def main_menu():
    keyboard = [
        [InlineKeyboardButton("📋 List All Licenses", callback_data='lic_list')],
        [InlineKeyboardButton("➕ Create New Key", callback_data='lic_create')],
        [InlineKeyboardButton("🔄 Reset Device ID", callback_data='lic_reset')],
        [InlineKeyboardButton("⏳ Extend Duration", callback_data='lic_extend')],
        [InlineKeyboardButton("🛡️ Change Status", callback_data='lic_status_menu')],
        [InlineKeyboardButton("❌ Delete Key", callback_data='lic_delete')]
    ]
    return InlineKeyboardMarkup(keyboard)

def status_menu():
    keyboard = [
        [InlineKeyboardButton("✅ Active", callback_data='status_active')],
        [InlineKeyboardButton("🚫 Revoked", callback_data='status_revoked')],
        [InlineKeyboardButton("🔙 Back", callback_data='main_menu')]
    ]
    return InlineKeyboardMarkup(keyboard)


# No other menus needed for now.

