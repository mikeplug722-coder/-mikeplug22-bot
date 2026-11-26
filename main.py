import logging, json, os, urllib.parse
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.environ.get("BOT_TOKEN", "PASTE_TOKEN_FROM_BOTFATHER_HERE")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "123456789"))

WHATSAPP_CHANNEL_1_LINK = "https://whatsapp.com/channel/0029Vb9NCWaE50UnoAsKgm0S"
WHATSAPP_CHANNEL_2_LINK = "https://whatsapp.com/channel/0029VbCEimNCXC3DUErxaq1z"
YOUTUBE_LINK = "https://www.youtube.com/@Mike_ai22"
ADMIN_WHATSAPP_NUMBER = "2348073579965"
DB_FILE = "verified.json"

def load_verified():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f: return set(json.load(f))
        except: return set()
    return set()

def save_verified():
    with open(DB_FILE, "w") as f: json.dump(list(verified_users), f)

def get_display_name(user):
    return f"@{user.username}" if user.username else user.first_name

def whatsapp_link(service, display_name):
    text = f"Hi MIKEPLUG22 ACADEMIC SERVICES! I am {display_name}. I want to apply for {service}. Please send me price & requirements."
    return f"https://wa.me/{ADMIN_WHATSAPP_NUMBER}?text={urllib.parse.quote(text)}"

verified_users = load_verified()
waiting_for_screenshot = set()
screenshots_count = {}
logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    display_name = get_display_name(user)
    if user.id not in verified_users:
        try:
            await context.bot.send_message(chat_id=ADMIN_ID, text=f"🔔 NEW USER JOINED MIKEPLUG22!\n\n👤 Name: {user.first_name}\n🆔 Username: {display_name}\n🆔 Telegram ID: {user.id}")
        except: pass
    if user.id in verified_users:
        await update.message.reply_text(f"👋 Welcome back {display_name}!")
        await show_main_menu(update, context, is_start=True)
        return
    keyboard = [
        [InlineKeyboardButton("📢 Join WhatsApp Channel 1", url=WHATSAPP_CHANNEL_1_LINK)],
        [InlineKeyboardButton("📢 Join WhatsApp Channel 2", url=WHATSAPP_CHANNEL_2_LINK)],
        [InlineKeyboardButton("▶️ Subscribe YouTube @Mike_ai22", url=YOUTUBE_LINK)],
        [InlineKeyboardButton("✅ I Have Joined All 3", callback_data="i_joined")],
    ]
    await update.message.reply_text(f"👋 Hi {display_name}! Welcome! 🎉\n\nWelcome to **MIKEPLUG22 ACADEMIC SERVICES** 🎓🔌\n\nYour #1 Plug for JAMB, WAEC, Admission & NYSC.\n\nTo unlock, you MUST complete **ALL 3 TASKS**:\n\n1️⃣ Join WhatsApp Channel 1\n2️⃣ Join WhatsApp Channel 2\n3️⃣ Subscribe to YouTube @Mike_ai22\n\n**Step 1:** Join / Subscribe to all 3\n**Step 2:** Take 3 screenshots\n**Step 3:** Click 'I Have Joined All 3' and send the 3 screenshots", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def i_joined_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    waiting_for_screenshot.add(query.from_user.id)
    screenshots_count[query.from_user.id] = 0
    await query.edit_message_text(f"📸 **Hi {get_display_name(query.from_user)}, send your 3 screenshots**\n\n1️⃣ WhatsApp Channel 1 - FOLLOWING\n2️⃣ WhatsApp Channel 2 - FOLLOWING\n3️⃣ YouTube @Mike_ai22 - SUBSCRIBED\n\nSend them one by one. (0/3 sent)", parse_mode="Markdown")

async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    display_name = get_display_name(user)
    if user.id in verified_users: return
    if user.id not in waiting_for_screenshot:
        await update.message.reply_text("Please send /start first and click 'I Have Joined All 3'.")
        return
    screenshots_count[user.id] = screenshots_count.get(user.id, 0) + 1
    count = screenshots_count[user.id]
    if count < 3:
        await update.message.reply_text(f"✅ Thanks {display_name}! Screenshot {count}/3 received!\n\nNow send screenshot {count+1}/3.")
        return
    waiting_for_screenshot.remove(user.id)
    screenshots_count.pop(user.id, None)
    verified_users.add(user.id)
    save_verified()
    try:
        await context.bot.send_message(chat_id=ADMIN_ID, text=f"✅ USER VERIFIED - MIKEPLUG22!\n\n👤 Name: {user.first_name}\n🆔 Username: {display_name}\n🆔 Telegram ID: {user.id}")
    except: pass
    await update.message.reply_text(f"🎉 **Congratulations {display_name}! You are VERIFIED!**\n\nWelcome to MIKEPLUG22 ACADEMIC SERVICES!", parse_mode="Markdown")
    await show_main_menu(update, context, is_start=False)

async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, is_start=False):
    display_name = get_display_name(update.effective_user)
    text = f"🔌 **MIKEPLUG22 ACADEMIC SERVICES - MAIN MENU** 🎓\n\nHi {display_name}, what do you need today? Choose below:"
    keyboard = [[InlineKeyboardButton("📝 JAMB Registration", callback_data="jamb_reg")],[InlineKeyboardButton("📖 WAEC & NECO Registration", callback_data="waec_neco")],[InlineKeyboardButton("🎓 Admission Processing", callback_data="admission")],[InlineKeyboardButton("🇳🇬 NYSC Services", callback_data="nysc")],[InlineKeyboardButton("💬 Talk to Admin on WhatsApp", callback_data="admin")]]
    if is_start: await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    else: await context.bot.send_message(update.effective_chat.id, text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in verified_users:
        await update.message.reply_text("⛔ Not verified. Send /start")
        return
    await show_main_menu(update, context, is_start=True)

async def service_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.from_user.id not in verified_users:
        await query.edit_message_text("⛔ Not verified. Send /start")
        return
    data = query.data
    display_name = get_display_name(query.from_user)
    back_btn = [[InlineKeyboardButton("⬅️ Back to Menu", callback_data="back_menu")]]
    if data == "back_menu":
        await query.edit_message_text(f"🔌 **MIKEPLUG22 ACADEMIC SERVICES - MAIN MENU** 🎓\n\nHi {display_name}, what do you need today?", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📝 JAMB Registration", callback_data="jamb_reg")],[InlineKeyboardButton("📖 WAEC & NECO Registration", callback_data="waec_neco")],[InlineKeyboardButton("🎓 Admission Processing", callback_data="admission")],[InlineKeyboardButton("🇳🇬 NYSC Services", callback_data="nysc")],[InlineKeyboardButton("💬 Talk to Admin on WhatsApp", callback_data="admin")]]), parse_mode="Markdown")
        return
    if data == "jamb_reg":
        text = "📝 **JAMB REGISTRATION - MIKEPLUG22**\n\n✅ UTME & Direct Entry\n✅ ePIN / Profile Code\n✅ Correction / Change of Course\n✅ Result / Admission Letter\n\n👇 Click to Apply on WhatsApp:"
        kb = [[InlineKeyboardButton("📲 Apply JAMB UTME - WhatsApp", url=whatsapp_link("JAMB UTME Registration", display_name))],[InlineKeyboardButton("📲 Apply JAMB DE - WhatsApp", url=whatsapp_link("JAMB Direct Entry Registration", display_name))],[InlineKeyboardButton("📲 Correction / Change of Course", url=whatsapp_link("JAMB Correction", display_name))]] + back_btn
    elif data == "waec_neco":
        text = "📖 **WAEC & NECO REGISTRATION - MIKEPLUG22**\n\n✅ WAEC May/June & GCE\n✅ NECO June/July & GCE\n✅ Result Checking\n\n👇 Click to Apply:"
        kb = [[InlineKeyboardButton("📲 Apply WAEC - WhatsApp", url=whatsapp_link("WAEC Registration", display_name))],[InlineKeyboardButton("📲 Apply NECO - WhatsApp", url=whatsapp_link("NECO Registration", display_name))],[InlineKeyboardButton("📲 Check Result - WhatsApp", url=whatsapp_link("Result Checking", display_name))]] + back_btn
    elif data == "admission":
        text = "🎓 **ADMISSION PROCESSING - MIKEPLUG22**\n\n✅ Post-UTME Registration\n✅ O'Level Upload on CAPS\n✅ CAPS Checking & Acceptance\n\nWe follow up till you are admitted!\n\n👇 Click to Apply:"
        kb = [[InlineKeyboardButton("📲 Start Admission Processing - WhatsApp", url=whatsapp_link("Admission Processing", display_name))],[InlineKeyboardButton("📲 Check CAPS - WhatsApp", url=whatsapp_link("Check CAPS", display_name))]] + back_btn
    elif data == "nysc":
        text = "🇳🇬 **NYSC SERVICES - MIKEPLUG22**\n\n✅ Mobilization / Registration\n✅ Senate List Checking\n✅ Call-up Letter\n✅ PPA / Relocation Guide\n\n👇 Click to Apply:"
        kb = [[InlineKeyboardButton("📲 NYSC Registration - WhatsApp", url=whatsapp_link("NYSC Registration", display_name))],[InlineKeyboardButton("📲 Check Senate List - WhatsApp", url=whatsapp_link("NYSC Senate List", display_name))]] + back_btn
    elif data == "admin":
        text = f"💬 **TALK TO ADMIN - MIKEPLUG22**\n\nHi {display_name}, click below:\n\n📱 WhatsApp: +2348073579965"
        kb = [[InlineKeyboardButton("💬 Chat Admin on WhatsApp", url=whatsapp_link("General Enquiry", display_name))]] + back_btn
    else:
        text = "Service coming soon"; kb = back_btn
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("menu", menu_command))
    app.add_handler(CallbackQueryHandler(i_joined_handler, pattern="^i_joined$"))
    app.add_handler(CallbackQueryHandler(service_handler, pattern="^(jamb_reg|waec_neco|admission|nysc|admin|back_menu)"))
    app.add_handler(MessageHandler(filters.PHOTO, photo_handler))
    print("MIKEPLUG22 Bot Running")
    app.run_polling()

if __name__ == "__main__": main()
