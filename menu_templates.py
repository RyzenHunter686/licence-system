from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def main_menu():
    keyboard = [
        [InlineKeyboardButton("➕ Create New License", callback_data='lic:create')],
        [InlineKeyboardButton("📋 Browse Licenses", callback_data='lic:browse:0')],
        [InlineKeyboardButton("🛡️ Settings", callback_data='menu:settings')]
    ]
    return InlineKeyboardMarkup(keyboard)

def license_list_menu(licenses, page=0):
    keyboard = []
    # Create a button for each license
    for lic in licenses:
        key = lic.get('key', 'Unknown')
        name = lic.get('nickname', 'User')
        status_emoji = "✅" if lic.get('status') == 'active' else "🚫"
        keyboard.append([InlineKeyboardButton(f"{status_emoji} {name} ({key})", callback_data=f"lic:view:{key}")])
    
    # Navigation row
    nav_row = []
    if page > 0:
        nav_row.append(InlineKeyboardButton("⬅️ Prev", callback_data=f"lic:browse:{page-1}"))
    nav_row.append(InlineKeyboardButton("🏠 Main Menu", callback_data='menu:main'))
    if len(licenses) >= 10: # Assuming page size is 10
        nav_row.append(InlineKeyboardButton("Next ➡️", callback_data=f"lic:browse:{page+1}"))
    keyboard.append(nav_row)
    
    return InlineKeyboardMarkup(keyboard)

def license_detail_menu(key):
    keyboard = [
        [
            InlineKeyboardButton("🔄 Reset ID", callback_data=f"lic:rst:{key}"),
            InlineKeyboardButton("⏳ Extend", callback_data=f"lic:ext_ui:{key}")
        ],
        [
            InlineKeyboardButton("🛡️ Toggle Status", callback_data=f"lic:stt:{key}"),
            InlineKeyboardButton("❌ Delete Key", callback_data=f"lic:del_ui:{key}")
        ],
        [InlineKeyboardButton("🔙 Back to List", callback_data='lic:browse:0')]
    ]
    return InlineKeyboardMarkup(keyboard)

def confirmation_menu(action, key):
    keyboard = [
        [
            InlineKeyboardButton("✅ Confirm", callback_data=f"lic:{action}:{key}"),
            InlineKeyboardButton("❌ Cancel", callback_data=f"lic:view:{key}")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)
