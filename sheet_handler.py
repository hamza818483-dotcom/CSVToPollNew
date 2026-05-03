# ============================================================
#  handlers/sheet_handler.py  —  /sheet কমান্ড
#  CSV → Practice Sheet PDF (৫টি ফরম্যাট)
# ============================================================

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
from handlers.admin_handler import is_admin
from handlers.split_handler import get_csv
from utils.csv_helper import parse_csv_bytes
from utils.pdf_builder import build_pdf
from config import PDF_QUESTIONS_PER_PAGE

logger = logging.getLogger(__name__)

# format selection session
_SHEET_SESSION: dict = {}

FORMAT_INFO = {
    1: "উত্তর ডানে কলামে, ব্যাখ্যা বক্সে",
    2: "উত্তর MCQ এর নিচে, ব্যাখ্যা বক্সে",
    3: "পেইজের নিচে উত্তর+ব্যাখ্যা ছকে",
    4: "MCQ এর নিচে ব্যাখ্যা, ডানে উত্তর কলাম",
    5: "সব MCQ শেষে লম্বা বক্সে উত্তর+ব্যাখ্যা",
}

async def cmd_sheet(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_admin(uid):
        await update.message.reply_text("❌ অ্যাডমিন পারমিশন নেই।")
        return

    stored = get_csv(uid)
    if not stored:
        await update.message.reply_text("📎 আগে CSV ফাইল পাঠাও, তারপর /sheet দাও।")
        return

    rows, _ = parse_csv_bytes(stored["data"])
    if not rows:
        await update.message.reply_text("❌ CSV ফাইলে কোনো প্রশ্ন নেই।")
        return

    _SHEET_SESSION[uid] = {
        "rows":     rows,
        "filename": stored["filename"],
    }

    # ফরম্যাট বাটন
    keyboard = []
    for fmt_id, desc in FORMAT_INFO.items():
        keyboard.append([InlineKeyboardButton(
            f"⚡ Format-{fmt_id:02d}: {desc}",
            callback_data=f"sheet_fmt_{fmt_id}_{uid}"
        )])

    await update.message.reply_text(
        f"📋 {len(rows)}টি MCQ পাওয়া গেছে।\n\n*কোন ফরম্যাটে Practice Sheet চাও?*",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def sheet_format_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    parts = query.data.split("_")
    fmt   = int(parts[2])
    uid   = int(parts[3])

    if query.from_user.id != uid:
        await query.answer("এটা তোমার সেশন না।", show_alert=True)
        return

    session = _SHEET_SESSION.get(uid)
    if not session:
        await query.edit_message_text("❌ সেশন শেষ হয়ে গেছে। আবার /sheet দাও।")
        return

    await query.edit_message_text(
        f"⏳ Format-{fmt:02d} তে PDF তৈরি হচ্ছে...\n"
        f"({len(session['rows'])}টি প্রশ্ন)"
    )

    try:
        pdf_bytes = build_pdf(
            rows    = session["rows"],
            fmt     = fmt,
            topic   = session["filename"].replace(".csv",""),
            qpp     = PDF_QUESTIONS_PER_PAGE,
        )
        base_name = session["filename"].replace(".csv","")
        pdf_name  = f"{base_name}_format{fmt}.pdf"

        await query.message.reply_document(
            document = pdf_bytes,
            filename = pdf_name,
            caption  = (
                f"✅ Practice Sheet তৈরি!\n"
                f"📌 ফরম্যাট: {fmt} — {FORMAT_INFO[fmt]}\n"
                f"📊 মোট প্রশ্ন: {len(session['rows'])}\n"
                f"📄 ফাইল: `{pdf_name}`"
            ),
            parse_mode="Markdown"
        )
        await query.edit_message_text(f"✅ Format-{fmt} PDF পাঠানো হয়েছে!")
    except Exception as e:
        logger.error(f"PDF build error: {e}", exc_info=True)
        await query.edit_message_text(f"❌ PDF তৈরিতে সমস্যা: {e}")
