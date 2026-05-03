# ============================================================
#  handlers/file_handler.py  —  ফাইল রিসিভার
#  CSV এবং PDF ফাইল গ্রহণ করে session এ রাখে
# ============================================================

import io
import logging
from telegram import Update
from telegram.ext import ContextTypes
from handlers.admin_handler import is_admin
from handlers.split_handler import store_csv

logger = logging.getLogger(__name__)

async def handle_document(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_admin(uid):
        return   # অ্যাডমিন না হলে ignore

    doc = update.message.document
    if not doc:
        return

    fname = doc.file_name or ""

    # CSV ফাইল
    if fname.lower().endswith(".csv"):
        msg = await update.message.reply_text("⏳ CSV লোড হচ্ছে...")
        try:
            file_obj = await ctx.bot.get_file(doc.file_id)
            buf = io.BytesIO()
            await file_obj.download_to_memory(buf)
            data = buf.getvalue()

            # validation
            from utils.csv_helper import parse_csv_bytes
            rows, headers = parse_csv_bytes(data)
            required = {"questions", "answer"}
            missing  = required - set(h.lower() for h in headers)

            if missing:
                await msg.edit_text(
                    f"⚠️ CSV তে এই কলামগুলো নেই: `{'`, `'.join(missing)}`\n"
                    f"পাওয়া কলাম: `{'`, `'.join(headers)}`",
                    parse_mode="Markdown"
                )
                return

            store_csv(uid, data, fname)
            await msg.edit_text(
                f"✅ CSV লোড হয়েছে!\n"
                f"📊 মোট প্রশ্ন: {len(rows)}\n"
                f"📋 কলাম: `{'`, `'.join(headers)}`\n\n"
                f"এখন `/sheet`, `/split` বা `/csv` কমান্ড দাও।",
                parse_mode="Markdown"
            )
        except Exception as e:
            logger.error(f"CSV load error: {e}", exc_info=True)
            await msg.edit_text(f"❌ CSV লোডে সমস্যা: {e}")

    # PDF ফাইল — watermark এর জন্য hint
    elif fname.lower().endswith(".pdf"):
        await update.message.reply_text(
            f"📄 PDF পেয়েছি: `{fname}`\n\n"
            f"ওয়াটারমার্ক দিতে:\n"
            f"• এই মেসেজটি reply করে `/wm তোমার নাম` লেখো\n"
            f"• অথবা reply করে `/wmp` (লোগো ওয়াটারমার্ক)",
            parse_mode="Markdown"
        )
