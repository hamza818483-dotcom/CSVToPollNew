#!/usr/bin/env python3
# ============================================================
#  bot.py  —  Atlas Bot মেইন ফাইল
#
#  নতুন হ্যান্ডলার এড করতে:
#   1. handlers/ ফোল্ডারে নতুন ফাইল বানাও
#   2. নিচে register_handlers() এ এড করো
#   3. শেষ!  (DEVELOPER_GUIDE.md দেখো)
# ============================================================

import os
import sys
import logging
import subprocess

# ── Auto-install libraries ────────────────────────────────
def pip_install(*pkgs):
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "--quiet", *pkgs]
    )

REQUIRED = [
    "python-telegram-bot==20.7",
    "reportlab",
    "PyMuPDF",
    "Pillow",
]
try:
    import telegram, reportlab, fitz, PIL
except ImportError:
    print("📦 Dependencies ইনস্টল হচ্ছে...")
    pip_install(*REQUIRED)

# ── Imports ───────────────────────────────────────────────
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, filters
)
from config import BOT_TOKEN
from utils.font_manager import setup_fonts
from handlers.admin_handler import (
    load_admins, cmd_start, cmd_permit, cmd_restart
)
from handlers.file_handler import handle_document
from handlers.split_handler import cmd_split
from handlers.sheet_handler import cmd_sheet, sheet_format_callback
from handlers.poll_handler import (
    cmd_csv_poll, poll_channel_callback, cmd_add_channel
)
from handlers.watermark_handler import (
    cmd_wm, wm_position_callback,
    cmd_wmp, wmp_position_callback
)

logging.basicConfig(
    format  = "%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    level   = logging.INFO,
    handlers= [
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("data/bot.log", encoding="utf-8"),
    ]
)
logger = logging.getLogger(__name__)

# ── Directories ───────────────────────────────────────────
os.makedirs("data",  exist_ok=True)
os.makedirs("temp",  exist_ok=True)
os.makedirs("fonts", exist_ok=True)

# ============================================================
#  register_handlers()  ←  নতুন হ্যান্ডলার এখানে এড করো
# ============================================================
def register_handlers(app: Application):

    # ── Core ─────────────────────────────────────────────
    app.add_handler(CommandHandler("start",   cmd_start))
    app.add_handler(CommandHandler("restart", cmd_restart))
    app.add_handler(CommandHandler("permit",  cmd_permit))

    # ── CSV Tools ─────────────────────────────────────────
    app.add_handler(CommandHandler("split",   cmd_split))
    app.add_handler(CommandHandler("sheet",   cmd_sheet))
    app.add_handler(CommandHandler("csv",     cmd_csv_poll))

    # ── Poll ──────────────────────────────────────────────
    app.add_handler(CommandHandler("addchannel", cmd_add_channel))

    # ── Watermark ─────────────────────────────────────────
    app.add_handler(CommandHandler("wm",  cmd_wm))
    app.add_handler(CommandHandler("wmp", cmd_wmp))

    # ── File receiver (CSV / PDF) ─────────────────────────
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))

    # ── Callbacks (Inline buttons) ────────────────────────
    app.add_handler(CallbackQueryHandler(sheet_format_callback, pattern=r"^sheet_fmt_"))
    app.add_handler(CallbackQueryHandler(poll_channel_callback,  pattern=r"^poll_ch_"))
    app.add_handler(CallbackQueryHandler(wm_position_callback,   pattern=r"^wm_pos_"))
    app.add_handler(CallbackQueryHandler(wmp_position_callback,  pattern=r"^wmp_pos_"))

    # ── নতুন হ্যান্ডলার এখানে এড করো ─────────────────────
    # from handlers.my_new_handler import cmd_mycommand, my_callback
    # app.add_handler(CommandHandler("mycommand", cmd_mycommand))
    # app.add_handler(CallbackQueryHandler(my_callback, pattern=r"^my_prefix_"))

    logger.info("✅ সব হ্যান্ডলার রেজিস্টার হয়েছে।")

# ── Main ──────────────────────────────────────────────────
def main():
    logger.info("🚀 Atlas Bot শুরু হচ্ছে...")

    # ফন্ট লোড (একবার)
    fonts = setup_fonts()
    logger.info(f"🔤 ফন্ট: {fonts['regular']} / {fonts['bold']}")

    # অ্যাডমিন লোড
    load_admins()

    app = Application.builder().token(BOT_TOKEN).build()
    register_handlers(app)

    logger.info("✅ Bot চালু! Ctrl+C দিয়ে থামাও।")
    app.run_polling(
        poll_interval      = 1,
        timeout            = 30,
        drop_pending_updates = True,
    )

if __name__ == "__main__":
    main()
