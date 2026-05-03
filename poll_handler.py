# ============================================================
#  handlers/poll_handler.py  —  /csv কমান্ড
#  CSV → চ্যানেলে Quiz Poll পাঠানো
# ============================================================

import asyncio
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
from handlers.admin_handler import is_admin
from handlers.split_handler import get_csv
from utils.csv_helper import parse_csv_bytes, get_options, get_answer_label
from config import POLL_DELAY_SEC, POLL_IS_ANONYMOUS, POLL_TYPE

logger = logging.getLogger(__name__)

_POLL_SESSION: dict = {}

async def cmd_csv_poll(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_admin(uid):
        await update.message.reply_text("❌ অ্যাডমিন পারমিশন নেই।")
        return

    stored = get_csv(uid)
    if not stored:
        await update.message.reply_text("📎 আগে CSV ফাইল পাঠাও, তারপর /csv দাও।")
        return

    # pre-message = /csv এর পরে যা লিখেছ
    pre_msg = " ".join(ctx.args) if ctx.args else ""

    rows, _ = parse_csv_bytes(stored["data"])
    if not rows:
        await update.message.reply_text("❌ CSV ফাইলে কোনো প্রশ্ন নেই।")
        return

    _POLL_SESSION[uid] = {
        "rows":    rows,
        "pre_msg": pre_msg,
        "msg_id":  update.message.message_id,
        "chat_id": update.effective_chat.id,
    }

    # বট যে চ্যানেলগুলোতে অ্যাডমিন সেগুলো দেখাও
    # (চ্যানেল ম্যানুয়ালি যোগ করা)
    keyboard = await _build_channel_keyboard(ctx.bot, uid)
    if not keyboard:
        await update.message.reply_text(
            "❌ কোনো চ্যানেল পাওয়া যায়নি।\n"
            "বটকে যে চ্যানেলে পাঠাতে চাও সেখানে Admin করো,\n"
            "তারপর `/addchannel <channel_id>` দাও।",
            parse_mode="Markdown"
        )
        return

    await update.message.reply_text(
        f"📡 {len(rows)}টি প্রশ্ন পাওয়া গেছে।\n\n*কোন চ্যানেলে Poll পাঠাবো?*",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def _build_channel_keyboard(bot, uid):
    """channels.txt থেকে চ্যানেল লিস্ট বানাও।"""
    import os
    channels_file = "data/channels.txt"
    if not os.path.exists(channels_file):
        return []

    keyboard = []
    with open(channels_file) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            try:
                ch_id = int(line.split()[0])
                ch_name = " ".join(line.split()[1:]) or str(ch_id)
                # বট ওই চ্যানেলে অ্যাডমিন কিনা চেক
                try:
                    member = await bot.get_chat_member(ch_id, bot.id)
                    if member.status in ("administrator", "creator"):
                        keyboard.append([InlineKeyboardButton(
                            f"📢 {ch_name}",
                            callback_data=f"poll_ch_{ch_id}_{uid}"
                        )])
                except Exception:
                    pass
            except Exception:
                pass
    return keyboard

async def poll_channel_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    parts  = query.data.split("_")
    ch_id  = int(parts[2])
    uid    = int(parts[3])

    if query.from_user.id != uid:
        await query.answer("এটা তোমার সেশন না।", show_alert=True)
        return

    session = _POLL_SESSION.get(uid)
    if not session:
        await query.edit_message_text("❌ সেশন শেষ। আবার /csv দাও।")
        return

    rows    = session["rows"]
    pre_msg = session["pre_msg"]

    # টপিক নাম (CSV ফাইলের section বা প্রথম প্রশ্নের type)
    topic   = rows[0].get("section", rows[0].get("type", "MCQ")) if rows else "MCQ"

    await query.edit_message_text(
        f"🚀 {len(rows)}টি Poll পাঠানো শুরু হচ্ছে...\nচ্যানেল: `{ch_id}`",
        parse_mode="Markdown"
    )

    # pre-message আগে পাঠাও (reply হিসেবে সব poll যাবে এর নিচে)
    if pre_msg:
        pre_sent = await ctx.bot.send_message(ch_id, pre_msg)
        reply_to = pre_sent.message_id
    else:
        reply_to = None

    sent_count = 0
    errors     = 0

    for row in rows:
        opts = get_options(row)
        if not opts or len(opts) < 2:
            errors += 1
            continue
        # সর্বোচ্চ ১০টি অপশন (Telegram limit)
        opts = opts[:10]
        ans_label, _ = get_answer_label(row, opts)
        ans_idx      = ["A","B","C","D","E"].index(ans_label) if ans_label in "ABCDE" else 0

        q_text = row.get("questions","?").strip()[:300]

        try:
            await ctx.bot.send_poll(
                chat_id              = ch_id,
                question             = q_text,
                options              = opts,
                type                 = POLL_TYPE,
                correct_option_id    = ans_idx,
                explanation          = row.get("explanation","")[:200] or None,
                is_anonymous         = POLL_IS_ANONYMOUS,
                reply_to_message_id  = reply_to,
            )
            sent_count += 1
            await asyncio.sleep(POLL_DELAY_SEC)
        except Exception as e:
            logger.error(f"Poll send error: {e}")
            errors += 1

    # সমাপ্তি মেসেজ
    finish_text = (
        f"🎉 ধন্যবাদ!\n"
        f"এটলাস আয়োজিত *{topic}* টপিকে পোল সলভে অংশগ্রহণ করার জন্য। 🙌\n\n"
        f"📊 মোট পোল: *{sent_count}টি*\n\n"
        f"তোমার স্কোর কত? 🤔\n"
        f"( ? / {sent_count} )\n\n"
        f"নিচে লিখো! 👇"
    )

    if reply_to:
        await ctx.bot.send_message(
            ch_id, finish_text,
            parse_mode="Markdown",
            reply_to_message_id=reply_to
        )
    else:
        await ctx.bot.send_message(ch_id, finish_text, parse_mode="Markdown")

    summary = (
        f"✅ পাঠানো শেষ!\n"
        f"📤 পাঠানো হয়েছে: {sent_count}টি\n"
        + (f"⚠️ ত্রুটি: {errors}টি\n" if errors else "")
    )
    await query.edit_message_text(summary)

# ─── /addchannel ──────────────────────────────────────────
async def cmd_add_channel(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Owner: /addchannel -100xxxxxxxxx চ্যানেল নাম"""
    from config import OWNER_ID
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("❌ শুধু Owner পারবেন।")
        return
    if len(ctx.args) < 2:
        await update.message.reply_text(
            "ব্যবহার: `/addchannel -100xxxxxxxxx চ্যানেল নাম`",
            parse_mode="Markdown"
        )
        return
    import os
    ch_id   = ctx.args[0]
    ch_name = " ".join(ctx.args[1:])
    os.makedirs("data", exist_ok=True)
    with open("data/channels.txt", "a") as f:
        f.write(f"{ch_id} {ch_name}\n")
    await update.message.reply_text(f"✅ চ্যানেল যোগ হয়েছে: {ch_name} ({ch_id})")
