# ============================================================
#  handlers/split_handler.py  —  /split কমান্ড
#  CSV ফাইলকে ছোট ছোট ভাগে ভাগ করে
# ============================================================

import io
import csv
import zipfile
import logging
from telegram import Update
from telegram.ext import ContextTypes
from handlers.admin_handler import is_admin
from utils.csv_helper import parse_csv_bytes

logger = logging.getLogger(__name__)

# user_id -> bytes (শেষ আপলোড করা CSV)
_CSV_STORE: dict = {}

def store_csv(user_id: int, data: bytes, filename: str):
    _CSV_STORE[user_id] = {"data": data, "filename": filename}

def get_csv(user_id: int):
    return _CSV_STORE.get(user_id)

async def cmd_split(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_admin(uid):
        await update.message.reply_text("❌ অ্যাডমিন পারমিশন নেই।")
        return

    stored = get_csv(uid)
    if not stored:
        await update.message.reply_text("📎 আগে একটি CSV ফাইল পাঠাও, তারপর /split দাও।")
        return

    if not ctx.args or not ctx.args[0].isdigit():
        await update.message.reply_text("ব্যবহার: `/split 20`  (প্রতি ভাগে ২০টি প্রশ্ন)", parse_mode="Markdown")
        return

    n = int(ctx.args[0])
    rows, headers = parse_csv_bytes(stored["data"])

    if not rows:
        await update.message.reply_text("❌ CSV ফাইলে কোনো তথ্য নেই।")
        return

    total_parts = (len(rows) + n - 1) // n
    base_name   = stored["filename"].replace(".csv", "")

    msg = await update.message.reply_text(
        f"⏳ {len(rows)}টি প্রশ্নকে {total_parts}টি ভাগে ভাগ করছি...")

    # সব ফাইল zip করে পাঠাও
    zip_buf = io.BytesIO()
    with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for i in range(total_parts):
            chunk = rows[i*n : (i+1)*n]
            csv_buf = io.StringIO()
            writer  = csv.DictWriter(csv_buf, fieldnames=headers)
            writer.writeheader()
            writer.writerows(chunk)
            fname = f"{base_name}_part{i+1:02d}.csv"
            zf.writestr(fname, csv_buf.getvalue().encode("utf-8-sig"))

    zip_buf.seek(0)
    await msg.delete()
    await update.message.reply_document(
        document    = zip_buf,
        filename    = f"{base_name}_split.zip",
        caption     = (f"✅ সম্পন্ন!\n"
                       f"📊 মোট প্রশ্ন: {len(rows)}\n"
                       f"📁 মোট ভাগ: {total_parts}\n"
                       f"📝 প্রতি ভাগে: {n}টি")
    )
