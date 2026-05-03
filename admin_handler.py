# ============================================================
#  handlers/admin_handler.py  —  /permit, /start
#  নতুন অ্যাডমিন কমান্ড এখানে এড করো
# ============================================================

from telegram import Update
from telegram.ext import ContextTypes
from config import OWNER_ID, ADMINS_FILE
import os

# ─── Admin Store ─────────────────────────────────────────
_ADMINS: set = set()

def load_admins():
    global _ADMINS
    _ADMINS = {OWNER_ID}
    if os.path.exists(ADMINS_FILE):
        with open(ADMINS_FILE) as f:
            for line in f:
                try: _ADMINS.add(int(line.strip()))
                except: pass

def save_admins():
    os.makedirs(os.path.dirname(ADMINS_FILE), exist_ok=True)
    with open(ADMINS_FILE, "w") as f:
        for uid in _ADMINS:
            if uid != OWNER_ID:
                f.write(f"{uid}\n")

def is_admin(user_id: int) -> bool:
    return user_id in _ADMINS

# ─── /start ──────────────────────────────────────────────
async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    text = (
        "👋 *Atlas Bot এ স্বাগতম!*\n\n"
        "📌 *সব কমান্ড:*\n\n"
        "🔴 *CSV ফাইল টুলস*\n"
        "`/split <number>` — CSV ভাগ করো (প্রতি ভাগে N প্রশ্ন)\n"
        "`/sheet` — CSV থেকে Practice Sheet PDF\n"
        "`/csv [pre-message]` — CSV থেকে চ্যানেলে Poll পাঠাও\n\n"
        "🟡 *ওয়াটারমার্ক*\n"
        "`/wm <নাম>` — PDF তে টেক্সট ওয়াটারমার্ক\n"
        "`/wmp` — PDF তে লোগো ওয়াটারমার্ক\n\n"
        "🟢 *অ্যাডমিন* (Owner only)\n"
        "`/permit <user_id>` — কাউকে অ্যাডমিন বানাও\n\n"
        "🔵 *অন্যান্য*\n"
        "`/restart` — বট রিস্টার্ট (PythonAnywhere)\n"
        "`/start` — এই মেনু\n\n"
        "📎 CSV ফাইল পাঠানোর পর কমান্ড দাও।"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

# ─── /permit ─────────────────────────────────────────────
async def cmd_permit(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("❌ শুধু Owner এই কমান্ড ব্যবহার করতে পারবেন।")
        return
    if not ctx.args:
        await update.message.reply_text("ব্যবহার: `/permit <user_id>`", parse_mode="Markdown")
        return
    try:
        uid = int(ctx.args[0])
        _ADMINS.add(uid)
        save_admins()
        await update.message.reply_text(f"✅ User `{uid}` কে অ্যাডমিন করা হয়েছে।", parse_mode="Markdown")
    except ValueError:
        await update.message.reply_text("❌ সঠিক User ID দাও।")

# ─── /restart ────────────────────────────────────────────
async def cmd_restart(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ অ্যাডমিন পারমিশন নেই।")
        return
    await update.message.reply_text("🔄 বট রিস্টার্ট হচ্ছে...")
    import os, sys
    os.execv(sys.executable, [sys.executable] + sys.argv)
