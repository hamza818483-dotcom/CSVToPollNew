# 🛠️ DEVELOPER GUIDE — Atlas Bot

## ফোল্ডার স্ট্রাকচার

```
atlas_bot/
│
├── bot.py              ← মেইন ফাইল (এখানে হ্যান্ডলার রেজিস্টার হয়)
├── config.py           ← সব সেটিংস (token, delay, opacity ইত্যাদি)
├── requirements.txt
│
├── handlers/           ← প্রতিটি ফিচার আলাদা ফাইলে
│   ├── admin_handler.py     (/start, /permit, /restart)
│   ├── file_handler.py      (CSV/PDF রিসিভ)
│   ├── split_handler.py     (/split)
│   ├── sheet_handler.py     (/sheet)
│   ├── poll_handler.py      (/csv)
│   └── watermark_handler.py (/wm, /wmp)
│
├── utils/              ← helper functions
│   ├── font_manager.py      (বাংলা+ইংলিশ ফন্ট)
│   ├── pdf_builder.py       (Practice Sheet PDF)
│   ├── csv_helper.py        (CSV parse)
│   └── watermark.py         (ওয়াটারমার্ক)
│
├── data/               ← runtime data
│   ├── admins.txt
│   ├── channels.txt
│   └── bot.log
│
└── fonts/              ← ফন্ট ফাইল (auto-download হয়)
```

---

## ✅ নতুন কমান্ড এড করতে (মাত্র ৩ ধাপ)

### ধাপ ১: `handlers/` এ নতুন ফাইল বানাও

```python
# handlers/my_feature.py
from telegram import Update
from telegram.ext import ContextTypes
from handlers.admin_handler import is_admin

async def cmd_mycommand(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_admin(uid):
        await update.message.reply_text("❌ অ্যাডমিন পারমিশন নেই।")
        return
    await update.message.reply_text("আমার নতুন ফিচার!")
```

### ধাপ ২: `bot.py` তে `register_handlers()` এ এড করো

```python
from handlers.my_feature import cmd_mycommand
app.add_handler(CommandHandler("mycommand", cmd_mycommand))
```

### ধাপ ৩: `/start` মেসেজে কমান্ড লিস্টে এড করো (admin_handler.py)

---

## ✅ নতুন PDF ফরম্যাট এড করতে (মাত্র ২ ধাপ)

### ধাপ ১: `utils/pdf_builder.py` তে ফাংশন বানাও

```python
def _build_format_6(rows, topic, qpp):
    story = _page_header(topic)
    # তোমার কাস্টম লেআউট...
    return story
```

### ধাপ ২: `FORMAT_BUILDERS` dict এ এড করো

```python
FORMAT_BUILDERS = {
    1: _build_format_1,
    ...
    6: _build_format_6,  # ← এড করো
}
```

শেষ! `sheet_handler.py` বা `bot.py` তে হাত দিতে হবে না।

---

## ✅ নতুন ফন্ট এড করতে

`config.py` বা `bot.py` তে `main()` এর শুরুতে:

```python
from utils.font_manager import add_custom_font
add_custom_font(
    "MyFont",      "fonts/MyFont-Regular.ttf",
    "MyFont-Bold", "fonts/MyFont-Bold.ttf"
)
```

---

## ✅ নতুন চ্যানেল এড করতে

বটে মেসেজ করো:
```
/addchannel -1001234567890 আমার চ্যানেলের নাম
```

---

## ✅ CSV ফরম্যাট

```
questions,option1,option2,option3,option4,option5,answer,explanation,type,section
```

- `option5` খালি রাখলে চলবে
- `answer` = 1,2,3,4,5 (number)
- `type` ও `section` = যেকোনো টেক্সট

---

## সেটিংস পরিবর্তন করতে

`config.py` খোলো — সব অপশন সেখানে আছে:
- `PDF_QUESTIONS_PER_PAGE` = প্রতি পেইজে প্রশ্ন
- `POLL_DELAY_SEC` = পোলের মাঝে বিরতি
- `WATERMARK_OPACITY` = ওয়াটারমার্কের হালকা/গাঢ়ত্ব
