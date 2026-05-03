# ============================================================
#  utils/font_manager.py  —  বাংলা + ইংলিশ ফন্ট ম্যানেজার
#  নতুন ফন্ট এড করতে: add_custom_font() ব্যবহার করো
# ============================================================

import os
import logging
import urllib.request
from pathlib import Path
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

logger = logging.getLogger(__name__)

_REGISTERED  = {}
_PRIMARY      = None
_PRIMARY_BOLD = None

# প্রতিটি ফন্টের জন্য একাধিক URL — একটি fail হলে পরেরটা চেষ্টা করে
FONT_SOURCES = {
    "NotoSansBengali-Regular": {
        "path": "fonts/NotoSansBengali-Regular.ttf",
        "urls": [
            "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSansBengali/NotoSansBengali-Regular.ttf",
            "https://raw.githubusercontent.com/notofonts/bengali/main/fonts/NotoSansBengali/unhinted/ttf/NotoSansBengali-Regular.ttf",
            "https://github.com/notofonts/noto-cjk/raw/main/Sans/OTF/Bengali/NotoSansBengali-Regular.otf",
        ]
    },
    "NotoSansBengali-Bold": {
        "path": "fonts/NotoSansBengali-Bold.ttf",
        "urls": [
            "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSansBengali/NotoSansBengali-Bold.ttf",
            "https://raw.githubusercontent.com/notofonts/bengali/main/fonts/NotoSansBengali/unhinted/ttf/NotoSansBengali-Bold.ttf",
        ]
    },
    "HindSiliguri-Regular": {
        "path": "fonts/HindSiliguri-Regular.ttf",
        "urls": [
            "https://github.com/googlefonts/hind-siliguri/raw/main/fonts/ttf/HindSiliguri-Regular.ttf",
            "https://github.com/itfoundry/hind-siliguri/raw/master/fonts/ttf/HindSiliguri-Regular.ttf",
        ]
    },
    "HindSiliguri-Bold": {
        "path": "fonts/HindSiliguri-Bold.ttf",
        "urls": [
            "https://github.com/googlefonts/hind-siliguri/raw/main/fonts/ttf/HindSiliguri-Bold.ttf",
            "https://github.com/itfoundry/hind-siliguri/raw/master/fonts/ttf/HindSiliguri-Bold.ttf",
        ]
    },
}

def _download(urls, dest: str) -> bool:
    """একাধিক URL চেষ্টা করে ফন্ট ডাউনলোড করে।"""
    if isinstance(urls, str):
        urls = [urls]
    Path(dest).parent.mkdir(parents=True, exist_ok=True)
    for url in urls:
        try:
            logger.info(f"Downloading: {url[:70]}")
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=20) as r, open(dest, "wb") as f:
                f.write(r.read())
            if os.path.exists(dest) and os.path.getsize(dest) > 10_000:
                logger.info(f"Font saved: {dest}")
                return True
        except Exception as e:
            logger.warning(f"Failed ({url[:50]}): {e}")
            if os.path.exists(dest):
                os.remove(dest)
    return False

def _register(name: str, path: str) -> bool:
    try:
        pdfmetrics.registerFont(TTFont(name, path))
        _REGISTERED[name] = path
        return True
    except Exception as e:
        logger.warning(f"Register failed ({name}): {e}")
        return False

def _try_font(name: str) -> bool:
    if name in _REGISTERED:
        return True
    cfg  = FONT_SOURCES.get(name, {})
    path = cfg.get("path")
    urls = cfg.get("urls", [])
    if not path:
        return False
    if os.path.exists(path) and os.path.getsize(path) > 10_000:
        return _register(name, path)
    if _download(urls, path):
        return _register(name, path)
    return False

def setup_fonts() -> dict:
    """
    বট স্টার্টে একবার কল করো।
    Priority: NotoSansBengali > HindSiliguri > Helvetica (fallback)
    """
    global _PRIMARY, _PRIMARY_BOLD

    # ১. Noto Sans Bengali
    if _try_font("NotoSansBengali-Regular") and _try_font("NotoSansBengali-Bold"):
        _PRIMARY, _PRIMARY_BOLD = "NotoSansBengali-Regular", "NotoSansBengali-Bold"
        logger.info("Font loaded: Noto Sans Bengali")

    # ২. Hind Siliguri (fallback)
    elif _try_font("HindSiliguri-Regular") and _try_font("HindSiliguri-Bold"):
        _PRIMARY, _PRIMARY_BOLD = "HindSiliguri-Regular", "HindSiliguri-Bold"
        logger.info("Font loaded: Hind Siliguri")

    # ৩. System fallback (বাংলা দেখাবে না কিন্তু ক্র্যাশ করবে না)
    else:
        _PRIMARY, _PRIMARY_BOLD = "Helvetica", "Helvetica-Bold"
        logger.warning("No Bengali font! Using Helvetica. Put a TTF in fonts/ folder.")

    return {"regular": _PRIMARY, "bold": _PRIMARY_BOLD, "fallback": "Helvetica"}

def get_font(bold: bool = False) -> str:
    """PDF স্টাইলে ব্যবহার করো।"""
    if _PRIMARY is None:
        setup_fonts()
    return _PRIMARY_BOLD if bold else _PRIMARY

def add_custom_font(name: str, path: str, bold_name: str = None, bold_path: str = None):
    """
    নিজের ফন্ট এড করতে (bot.py এর main() এ কল করো):
        from utils.font_manager import add_custom_font
        add_custom_font("MyFont", "fonts/MyFont.ttf", "MyFont-Bold", "fonts/MyFont-Bold.ttf")
    """
    global _PRIMARY, _PRIMARY_BOLD
    if os.path.exists(path) and _register(name, path):
        _PRIMARY = name
        logger.info(f"Custom font activated: {name}")
    if bold_name and bold_path and os.path.exists(bold_path) and _register(bold_name, bold_path):
        _PRIMARY_BOLD = bold_name

def install_font_from_file(ttf_path: str, name: str = None, make_primary: bool = True):
    """
    নিজে ফন্ট ফাইল আপলোড করে এই ফাংশন দিয়ে লোড করতে পারো।
    PythonAnywhere এ fonts/ ফোল্ডারে .ttf ফাইল রাখো।
    """
    if not name:
        name = Path(ttf_path).stem
    if _register(name, ttf_path) and make_primary:
        global _PRIMARY
        _PRIMARY = name
        logger.info(f"Font installed: {name} from {ttf_path}")
