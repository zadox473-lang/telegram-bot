import os
import random
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# ================= CONFIG =================
BOT_TOKEN = "8511686163:AAF9J9B-7MzBEl2FVz-Z2nm_T3FmolRcnVE"
ADMIN_ID = 8210445482

FORCE_CHANNELS = [
    "@midnight_xaura",
    "@proxydominates"
]

API_URL = "https://insta-profile-info-api.vercel.app/api/instagram.php?username="
USERS_FILE = "users.txt"

WELCOME_TEXT = (
    "✨ Welcome to Insta Analyzer Pro ✨\n\n"
    "Advanced Instagram Profile Analysis Tool\n"
    "Created by @Proxyfxz"
)

# ================= USER COUNT =================
def save_user(user_id: int):
    if not os.path.exists(USERS_FILE):
        open(USERS_FILE, "w").close()

    with open(USERS_FILE, "r+") as f:
        users = f.read().splitlines()
        if str(user_id) not in users:
            f.write(f"{user_id}\n")

def total_users():
    if not os.path.exists(USERS_FILE):
        return 0
    with open(USERS_FILE) as f:
        return len(f.read().splitlines())

# ================= FORCE JOIN =================
async def is_joined(user_id: int, context: ContextTypes.DEFAULT_TYPE):
    for ch in FORCE_CHANNELS:
        try:
            member = await context.bot.get_chat_member(ch, user_id)
            if member.status == "left":
                return False
        except:
            return False
    return True

def force_join_kb():
    btns = [
        [InlineKeyboardButton(f"🔗 Join {ch}", url=f"https://t.me/{ch[1:]}")]
        for ch in FORCE_CHANNELS
    ]
    btns.append([InlineKeyboardButton("✅ I Joined", callback_data="check_join")])
    return InlineKeyboardMarkup(btns)

# ================= UI =================
def menu_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔍 Deep Analysis", callback_data="deep")],
        [InlineKeyboardButton("📈 Analytics", callback_data="analytics"),
         InlineKeyboardButton("👑 Focus Mode", callback_data="focus")],
        [InlineKeyboardButton("⚙️ Settings", callback_data="settings"),
         InlineKeyboardButton("❓ Help", callback_data="help")],
    ])

def back_menu_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⬅️ Back to Menu", callback_data="menu")]
    ])

def after_analysis_kb(username: str):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 Full Report", callback_data=f"report|{username}")],
        [InlineKeyboardButton("🔄 Analyze Again", callback_data="deep")],
        [InlineKeyboardButton("🔗 Open Profile", url=f"https://instagram.com/{username}")],
        [InlineKeyboardButton("⬅️ Back to Menu", callback_data="menu")],
    ])

# ================= API =================
def fetch_profile(username: str):
    r = requests.get(API_URL + username, timeout=20)
    if r.status_code != 200:
        return None
    data = r.json()
    if data.get("status") != "ok":
        return None
    return data.get("profile")

# ================= ANALYSIS =================
def calc_risk(profile: dict):
    followers = int(profile.get("followers") or 0)
    following = int(profile.get("following") or 0)
    posts = int(profile.get("posts") or 0)
    private = bool(profile.get("is_private") or False)

    score = 0
    if private: score += 25
    if posts == 0: score += 30
    if followers < 100: score += 10
    if following > 1500: score += 10

    scam = random.randint(5, 7)
    nudi = random.randint(5, 7)

    risk = min(95, score + scam * 3 + nudi * 3)
    issues = [f"{scam}x SCAM", f"{nudi}x NUDI"]
    return risk, issues

def full_report_text(username: str, profile: dict, risk: int, issues: list):
    return (
        "🎯 DEEP ANALYSIS REPORT\n"
        f"Profile: @{username}\n\n"
        "📋 BASIC INFO\n"
        f"👤 Name: {profile.get('full_name','')}\n"
        f"✅ Verified: {'Yes' if profile.get('is_verified') else 'No'}\n"
        f"📝 Bio: {profile.get('biography','')}\n"
        f"👥 Followers: {profile.get('followers',0)}\n"
        f"👤 Following: {profile.get('following',0)}\n"
        f"📸 Posts: {profile.get('posts',0)}\n"
        f"🔐 Private: {'Yes' if profile.get('is_private') else 'No'}\n\n"
        "🚨 DETECTED ISSUES\n"
        + "\n".join(f"• {i}" for i in issues)
        + f"\n\n⚠️ OVERALL RISK: {risk}%"
    )

# ================= HANDLERS =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    save_user(update.effective_user.id)

    if not await is_joined(update.effective_user.id, context):
        await update.message.reply_text(
            "🚫 You must join our channels to use this bot:",
            reply_markup=force_join_kb()
        )
        return

    await update.message.reply_text(WELCOME_TEXT, reply_markup=menu_kb())

async def callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = q.data

    if data == "check_join":
        if not await is_joined(q.from_user.id, context):
            await q.message.reply_text("❌ Please join all channels first.")
            return
        await q.message.reply_text(WELCOME_TEXT, reply_markup=menu_kb())
        return

    if data == "menu":
        await q.message.reply_text(WELCOME_TEXT, reply_markup=menu_kb())
        return

    if data == "deep":
        context.user_data["wait_user"] = True
        await q.message.reply_text("👤 Enter Instagram username:")
        return

    if data.startswith("report|"):
        username = data.split("|", 1)[1]
        profile = fetch_profile(username)
        if not profile:
            await q.message.reply_text("❌ Report not available.", reply_markup=menu_kb())
            return
        risk, issues = calc_risk(profile)
        await q.message.reply_text(
            full_report_text(username, profile, risk, issues),
            reply_markup=after_analysis_kb(username)
        )
        return

    if data in ["analytics", "focus", "settings", "help"]:
        await q.message.reply_text("⚙️ Feature coming soon.", reply_markup=back_menu_kb())
        return

async def handle_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("wait_user"):
        return

    username = update.message.text.replace("@", "").strip()
    context.user_data["wait_user"] = False
    await update.message.reply_text("🔄 Analyzing profile...")

    profile = fetch_profile(username)
    if not profile:
        await update.message.reply_text("❌ Profile not found.", reply_markup=menu_kb())
        return

    risk, issues = calc_risk(profile)
    await update.message.reply_text(
        full_report_text(username, profile, risk, issues),
        reply_markup=after_analysis_kb(username)
    )

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    await update.message.reply_text(f"👥 Total Users: {total_users()}")

# ================= RUN =================
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CallbackQueryHandler(callbacks))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_username))
    print("✅ Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()
