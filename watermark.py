# ============================================================
#  utils/watermark.py  —  টেক্সট ও লোগো ওয়াটারমার্ক
# ============================================================

import io
import math
import logging
import fitz   # PyMuPDF

logger = logging.getLogger(__name__)

POSITIONS = {
    "center":       ("center",  "center"),
    "top-right":    ("right",   "top"),
    "top-left":     ("left",    "top"),
    "bottom-right": ("right",   "bottom"),
    "bottom-left":  ("left",    "bottom"),
}

def _place_xy(rect, w, h, pos):
    """pos: (h_align, v_align)"""
    ha, va = pos
    pw, ph = rect.width, rect.height
    margin = 30
    x = margin if ha == "left" else (pw - w - margin if ha == "right" else (pw - w) / 2)
    y = margin if va == "top"  else (ph - h - margin if va == "bottom" else (ph - h) / 2)
    return x, y

def add_text_watermark(pdf_bytes: bytes, text: str,
                        opacity: float = 0.15,
                        position: str = "center",
                        font_size: int = 48) -> bytes:
    """প্রতিটি পেইজের মাঝে হালকা টেক্সট ওয়াটারমার্ক।"""
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        pos = POSITIONS.get(position, POSITIONS["center"])

        for page in doc:
            rect = page.rect
            # ডায়াগোনাল রোটেশন শুধু center এ
            angle = -30 if pos == ("center","center") else 0
            page.insert_text(
                fitz.Point(rect.width/2, rect.height/2),
                text,
                fontsize  = font_size,
                rotate    = angle,
                color     = (0, 0, 0),
                fill_opacity = opacity,
                overlay   = True,
            )
        buf = io.BytesIO()
        doc.save(buf)
        return buf.getvalue()
    except Exception as e:
        logger.error(f"Text watermark error: {e}")
        return pdf_bytes

def add_logo_watermark(pdf_bytes: bytes, logo_bytes: bytes,
                        position: str = "center",
                        opacity: float = 0.15,
                        size_px: int = 120) -> bytes:
    """প্রতিটি পেইজে লোগো ওয়াটারমার্ক।"""
    try:
        from PIL import Image
        import io as _io

        # লোগো রিসাইজ
        img = Image.open(_io.BytesIO(logo_bytes)).convert("RGBA")
        img.thumbnail((size_px, size_px), Image.LANCZOS)

        # ওপাসিটি অ্যাপ্লাই
        r, g, b, a = img.split()
        a = a.point(lambda x: int(x * opacity))
        img.putalpha(a)

        png_buf = _io.BytesIO()
        img.save(png_buf, "PNG")
        png_bytes = png_buf.getvalue()

        doc  = fitz.open(stream=pdf_bytes, filetype="pdf")
        pos  = POSITIONS.get(position, POSITIONS["center"])

        for page in doc:
            rect = page.rect
            x, y = _place_xy(rect, size_px, size_px, pos)
            img_rect = fitz.Rect(x, y, x + size_px, y + size_px)
            page.insert_image(img_rect, stream=png_bytes, overlay=True)

        buf = io.BytesIO()
        doc.save(buf)
        return buf.getvalue()
    except Exception as e:
        logger.error(f"Logo watermark error: {e}")
        return pdf_bytes
