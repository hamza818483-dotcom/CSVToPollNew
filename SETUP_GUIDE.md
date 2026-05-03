# 🚀 GitHub + PythonAnywhere সেটআপ গাইড
## Atlas Telegram Bot

---

## 📌 কী কী লাগবে?
- GitHub অ্যাকাউন্ট (ফ্রি): github.com
- PythonAnywhere অ্যাকাউন্ট (ফ্রি): pythonanywhere.com
- বটের ফাইলগুলো (atlas_bot ফোল্ডার)

**তোমাকে নতুন কিছু কিনতে হবে না। দুটোই সম্পূর্ণ ফ্রি।**

---

## ━━━━━━━━━━━━━━━━━━━━━━━━
## PART 1 — GitHub সেটআপ
## ━━━━━━━━━━━━━━━━━━━━━━━━

### ধাপ ১: GitHub অ্যাকাউন্ট বানাও
1. github.com এ যাও
2. "Sign up" ক্লিক করো
3. Email, username, password দিয়ে অ্যাকাউন্ট বানাও

### ধাপ ২: নতুন Repository বানাও
1. GitHub এ login করো
2. উপরে ডানে "+" → "New repository" ক্লিক করো
3. Repository name: `atlas-bot` (যেকোনো নাম দিতে পারো)
4. **Private** সিলেক্ট করো (বট টোকেন গোপন রাখতে)
5. "Create repository" ক্লিক করো

### ধাপ ৩: ফাইল আপলোড করো
GitHub repository খোলার পর:
1. "uploading an existing file" লিংকে ক্লিক করো
2. এই ফাইলগুলো আপলোড করো:
   ```
   bot.py
   config.py
   requirements.txt
   handlers/ (পুরো ফোল্ডার)
   utils/ (পুরো ফোল্ডার)
   DEVELOPER_GUIDE.md
   ```
   ⚠️ `data/` এবং `fonts/` আপলোড করতে হবে না (auto-create হবে)

3. "Commit changes" ক্লিক করো

### ধাপ ৪: .gitignore বানাও (Optional কিন্তু ভালো)
GitHub এ "Add file" → "Create new file"
নাম দাও: `.gitignore`
ভেতরে লেখো:
```
data/
fonts/
temp/
__pycache__/
*.pyc
*.log
```
"Commit" করো।

---

## ━━━━━━━━━━━━━━━━━━━━━━━━━━
## PART 2 — PythonAnywhere সেটআপ
## ━━━━━━━━━━━━━━━━━━━━━━━━━━

### ধাপ ১: অ্যাকাউন্ট বানাও
1. pythonanywhere.com এ যাও
2. "Start running Python online in less than a minute!" → Beginner account (ফ্রি)
3. Username, email, password দিয়ে রেজিস্টার করো

### ধাপ ২: Console খোলো
Login করার পর:
1. Dashboard এ "Consoles" ট্যাব
2. "Bash" ক্লিক করো
3. একটি terminal উইন্ডো খুলবে

### ধাপ ৩: GitHub থেকে কোড নামাও
Bash console এ টাইপ করো:

```bash
git clone https://github.com/তোমার_username/atlas-bot.git
cd atlas-bot
```

(তোমার GitHub username আর repo নাম দিয়ে বদলাও)

**Private repo হলে:**
```bash
git clone https://তোমার_username:তোমার_github_token@github.com/তোমার_username/atlas-bot.git
```
GitHub Token বানাতে: GitHub → Settings → Developer Settings → Personal Access Tokens → Generate New Token (repo permission দাও)

### ধাপ ৪: Dependencies ইনস্টল করো
```bash
cd atlas-bot
pip3.10 install -r requirements.txt --user
```
(কিছুক্ষণ সময় লাগবে)

### ধাপ ৫: ফোল্ডার বানাও
```bash
mkdir -p data fonts temp
```

### ধাপ ৬: বট টেস্ট করো (একবার)
```bash
python3.10 bot.py
```
যদি "Bot চালু!" দেখাও — সফল!
`Ctrl+C` দিয়ে থামাও।

---

## ━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## PART 3 — সবসময় চালু রাখা
## (Always-on Task)
## ━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**ফ্রি অ্যাকাউন্টে সবসময় চালু রাখার সরাসরি উপায় নেই।**
দুটো সমাধান আছে:

### সমাধান A — প্রতিদিন ম্যানুয়ালি চালাও (ফ্রি)
Bash console এ:
```bash
cd atlas-bot && python3.10 bot.py
```
Tab বন্ধ না করলে চলতে থাকবে।

**নিরাপদে Background এ চালাতে:**
```bash
cd atlas-bot
nohup python3.10 bot.py > data/bot.log 2>&1 &
echo "Bot PID: $!"
```
এখন tab বন্ধ করলেও চলবে। PID নোট করো।

**থামাতে:**
```bash
kill <PID_number>
# অথবা
pkill -f bot.py
```

### সমাধান B — PythonAnywhere Scheduled Task (ফ্রি)
১. Dashboard → "Tasks" ট্যাব
২. "Add a new scheduled task"
৩. Hour: `*/1` (প্রতি ঘন্টায়), অথবা Daily
৪. Command:
```bash
cd /home/তোমার_username/atlas-bot && python3.10 bot.py
```

### সমাধান C — Always On (Paid, $5/মাস)
১. Dashboard → "Tasks" → "Always-on tasks"
২. Command:
```bash
cd /home/তোমার_username/atlas-bot && python3.10 bot.py
```
এটাই সবচেয়ে ভালো — বট কখনো বন্ধ হবে না।

---

## ━━━━━━━━━━━━━━━━━━━━━━━━━━
## PART 4 — কোড আপডেট করা
## ━━━━━━━━━━━━━━━━━━━━━━━━━━

কোড পরিবর্তন করার পর:

### GitHub এ আপডেট করো:
1. GitHub এ গিয়ে ফাইল edit করো, অথবা
2. নতুন ফাইল আপলোড করো

### PythonAnywhere এ টান দাও:
```bash
cd atlas-bot
pkill -f bot.py        # আগের বট থামাও
git pull               # নতুন কোড নামাও
nohup python3.10 bot.py > data/bot.log 2>&1 &   # আবার চালু করো
```

---

## ━━━━━━━━━━━━━━━━━━━━━
## PART 5 — চ্যানেল যোগ করা
## ━━━━━━━━━━━━━━━━━━━━━

বট চালু হলে Telegram এ:
1. তোমার চ্যানেলে বটকে Admin করো
2. বটকে এই কমান্ড দাও:
```
/addchannel -1001234567890 আমার চ্যানেলের নাম
```
(চ্যানেল ID পেতে: @userinfobot এ চ্যানেল ফরোয়ার্ড করো)

---

## ━━━━━━━━━━━━━━━━━━━━━━
## PART 6 — সমস্যা হলে
## ━━━━━━━━━━━━━━━━━━━━━━

### লগ দেখতে:
```bash
tail -f atlas-bot/data/bot.log
```

### বট চলছে কিনা দেখতে:
```bash
ps aux | grep bot.py
```

### dependencies আবার ইনস্টল করতে:
```bash
pip3.10 install -r atlas-bot/requirements.txt --user --upgrade
```

### বট কাজ না করলে:
Telegram এ `/restart` দাও।
অথবা PythonAnywhere Bash এ:
```bash
pkill -f bot.py
cd atlas-bot && nohup python3.10 bot.py > data/bot.log 2>&1 &
```

---

## ✅ সংক্ষিপ্ত চেকলিস্ট

- [ ] GitHub অ্যাকাউন্ট বানানো
- [ ] Private repository বানানো
- [ ] সব ফাইল আপলোড করা
- [ ] PythonAnywhere অ্যাকাউন্ট বানানো
- [ ] Bash এ `git clone` করা
- [ ] `pip install -r requirements.txt` করা
- [ ] `python3.10 bot.py` দিয়ে টেস্ট করা
- [ ] চ্যানেলে বটকে Admin করা
- [ ] `/addchannel` দিয়ে চ্যানেল যোগ করা
- [ ] `/start` দিয়ে বট টেস্ট করা

---

## 📞 দরকারী লিংক

- Telegram Bot API: t.me/BotFather
- GitHub: github.com
- PythonAnywhere: pythonanywhere.com
- চ্যানেল ID পেতে: t.me/userinfobot
