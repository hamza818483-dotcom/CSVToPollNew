# ============================================================
#  config.py  —  Atlas Bot সব সেটিংস এখানে
#  নতুন কিছু এড করতে হলে শুধু এই ফাইল বদলাও
# ============================================================

BOT_TOKEN = "8757116951:AAGwrlY7ILI-i6-9tmzICjJI3mw6dk75xM0"
OWNER_ID  = 5341425626

# ── ফাইল পাথ ─────────────────────────────────────────────
ADMINS_FILE  = "data/admins.txt"
TEMP_DIR     = "temp"
FONT_DIR     = "fonts"

# ── PDF সেটিংস ───────────────────────────────────────────
PDF_QUESTIONS_PER_PAGE = 10   # প্রতি পেইজে কতটা MCQ
PDF_PAGE_SIZE = "A4"          # A4 বা LETTER
PDF_MARGIN_CM = 1.5

# ── Poll সেটিংস ──────────────────────────────────────────
POLL_DELAY_SEC = 2            # পোলের মধ্যে বিরতি (সেকেন্ড)
POLL_IS_ANONYMOUS = True      # Anonymous poll?
POLL_TYPE = "quiz"            # quiz বা regular

# ── Watermark সেটিংস ─────────────────────────────────────
WATERMARK_OPACITY   = 0.15    # 0.0–1.0 (হালকা রাখতে কম দাও)
WATERMARK_FONT_SIZE = 48
WATERMARK_COLOR     = (0, 0, 0)   # RGB

# ── নতুন কমান্ড এড করতে ──────────────────────────────────
# handlers/ ফোল্ডারে নতুন .py ফাইল বানাও
# তারপর bot.py তে register_handlers() এ এড করো
# বিস্তারিত: DEVELOPER_GUIDE.md দেখো
