# ============================================================
#  utils/pdf_builder.py  —  Practice Sheet PDF জেনারেটর
#  ফরম্যাট ১–৫ সাপোর্ট করে। বাংলা+ইংলিশ ফন্ট।
#
#  নতুন ফরম্যাট এড করতে:
#   1. _build_format_N() ফাংশন বানাও (নিচে দেখো)
#   2. FORMAT_BUILDERS dict এ এড করো
#   3. শেষ — অন্য কিছু বদলাতে হবে না
# ============================================================

import io
import logging
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.pdfgen import canvas as rl_canvas

from utils.font_manager import get_font
from utils.csv_helper import get_options, get_answer_label, circle

logger = logging.getLogger(__name__)

# ── পেইজ মাপ ─────────────────────────────────────────────
PAGE_W, PAGE_H = A4
MARGIN   = 1.5 * cm
COL_GAP  = 0.5 * cm
COL_W    = (PAGE_W - 2 * MARGIN - COL_GAP) / 2
FULL_W   = PAGE_W - 2 * MARGIN

# ── রঙ ────────────────────────────────────────────────────
C_BOX    = colors.HexColor("#EEF2FF")
C_ANS    = colors.HexColor("#E8F5E9")
C_LINE   = colors.HexColor("#CCCCCC")
C_HEADER = colors.HexColor("#1A237E")
C_SUB    = colors.HexColor("#555555")
C_WHITE  = colors.white
C_BLUE   = colors.HexColor("#0D47A1")
C_GREEN  = colors.HexColor("#1B5E20")

# ─── স্টাইল বিল্ডার ─────────────────────────────────────
def S(name, size=9, bold=False, color=None, align=TA_LEFT,
      leading=None, left=0, space_before=0, space_after=2):
    return ParagraphStyle(
        name,
        fontName   = get_font(bold),
        fontSize   = size,
        leading    = leading or (size * 1.45),
        textColor  = color or colors.black,
        alignment  = align,
        leftIndent = left,
        spaceBefore= space_before,
        spaceAfter = space_after,
        wordWrap   = "CJK",   # বাংলা word-wrap
    )

# ─── Page Number Canvas ───────────────────────────────────
class _PageNumCanvas(rl_canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._pages = []

    def showPage(self):
        self._pages.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        total = len(self._pages)
        for i, state in enumerate(self._pages, 1):
            self.__dict__.update(state)
            self._draw_num(i, total)
            super().showPage()
        super().save()

    def _draw_num(self, cur, total):
        self.saveState()
        self.setFont(get_font(False), 8)
        self.setFillColor(C_SUB)
        # নিচে ডানে
        self.drawRightString(PAGE_W - MARGIN, MARGIN * 0.55, f"{cur} / {total}")
        # নিচে বামে (পেইজ নম্বর)
        self.drawString(MARGIN, MARGIN * 0.55, f"Page {cur}")
        self.restoreState()

# ─── প্রশ্ন ব্লক বিল্ডার ─────────────────────────────────
def _q_block(idx, row, include_ans=False, include_exp=False,
             ans_inline=False):
    """
    একটি MCQ এর জন্য Flowable list রিটার্ন করে।
    include_ans  : অপশনের পরেই উত্তর দেখাবে?
    include_exp  : ব্যাখ্যা বক্স দেখাবে?
    ans_inline   : উত্তর ডানে (Format-01 কলাম লেআউট)?
    """
    elems = []
    opts  = get_options(row)
    if not opts:
        return elems

    ans_label, ans_text = get_answer_label(row, opts)
    exp_text = row.get("explanation", "").strip()
    q_text   = row.get("questions", f"প্রশ্ন {idx}").strip()

    sQ   = S(f"Q{idx}",   size=9,   bold=False)
    sOpt = S(f"O{idx}",   size=8.5, left=8)
    sAns = S(f"A{idx}",   size=8.5, bold=True,  color=C_BLUE)
    sExp = S(f"E{idx}",   size=8,   color=C_SUB)

    # প্রশ্ন
    elems.append(Paragraph(f"<b>{idx}.</b> {q_text}", sQ))

    # অপশন (A B C D গোল্লার ভেতর)
    for i, opt in enumerate(opts):
        label = ["A","B","C","D","E"][i]
        elems.append(Paragraph(f"{circle(label)} {opt}", sOpt))

    if include_ans and not ans_inline:
        elems.append(Paragraph(
            f"<b>✔ উত্তর:</b> {circle(ans_label)} {ans_text}", sAns))

    if include_exp and exp_text:
        box_data = [[Paragraph(
            ("<b>উত্তর:</b> " + circle(ans_label) + " " + ans_text + "<br/>"
             if include_ans else "") +
            f"<b>ব্যাখ্যা:</b> {exp_text}", sExp)]]
        tbl = Table(box_data, colWidths=[COL_W - 8])
        tbl.setStyle(TableStyle([
            ("BACKGROUND", (0,0),(-1,-1), C_BOX),
            ("BOX",        (0,0),(-1,-1), 0.5, C_LINE),
            ("TOPPADDING",    (0,0),(-1,-1), 4),
            ("BOTTOMPADDING", (0,0),(-1,-1), 4),
            ("LEFTPADDING",   (0,0),(-1,-1), 6),
            ("RIGHTPADDING",  (0,0),(-1,-1), 6),
        ]))
        elems.append(tbl)

    elems.append(Spacer(1, 4))
    return elems

def _divider():
    return HRFlowable(width=FULL_W, thickness=0.5, color=C_LINE,
                      spaceAfter=4, spaceBefore=4)

def _page_header(topic):
    sH = S("PH", size=13, bold=True, color=C_HEADER, align=TA_CENTER)
    sSub = S("PS", size=8, color=C_SUB, align=TA_CENTER)
    return [
        Paragraph("📘 Practice Sheet — Atlas", sH),
        Paragraph(topic, sSub),
        _divider(),
    ]

# ─── ২-কলাম লেআউট হেল্পার ────────────────────────────────
def _two_col(left_items, right_items):
    """বাম+ডান দুই কলামে ফ্লোয়েবল সাজায়।"""
    left_str  = "".join(_flowable_to_str(e) for e in left_items)
    right_str = "".join(_flowable_to_str(e) for e in right_items)
    # Table দিয়ে দুই কলাম
    data = [[left_items, right_items]]
    tbl  = Table(data, colWidths=[COL_W, COL_W])
    tbl.setStyle(TableStyle([
        ("VALIGN",      (0,0),(-1,-1), "TOP"),
        ("LEFTPADDING", (0,0),(-1,-1), 0),
        ("RIGHTPADDING",(0,0),(-1,-1), 0),
        ("TOPPADDING",  (0,0),(-1,-1), 0),
        ("BOTTOMPADDING",(0,0),(-1,-1), 0),
    ]))
    return tbl

# ─── FORMAT 1 ────────────────────────────────────────────
# উত্তর ডানে কলামে, ব্যাখ্যা MCQ এর নিচে বক্সে
def _build_format_1(rows, topic, qpp):
    story = _page_header(topic)
    sAnsCol = S("AC", size=8, bold=True, color=C_GREEN)
    sHdr    = S("AH", size=8, bold=True, color=C_HEADER)

    pages = [rows[i:i+qpp] for i in range(0, len(rows), qpp)]

    for p_idx, page in enumerate(pages):
        if p_idx > 0:
            story.append(PageBreak())
            story.append(_divider())

        n = len(page)
        half = math.ceil(n / 2)
        left_rows  = page[:half]
        right_rows = page[half:]

        left_q  = []
        right_q = []
        ans_col = [Paragraph("<b>উত্তর তালিকা</b>", sHdr), Spacer(1,4)]

        q_start = p_idx * qpp + 1
        for i, row in enumerate(left_rows, q_start):
            left_q += _q_block(i, row, include_exp=True)
            opts = get_options(row)
            al, at = get_answer_label(row, opts)
            ans_col.append(Paragraph(f"{i}. {circle(al)}", sAnsCol))

        rstart = q_start + half
        for i, row in enumerate(right_rows, rstart):
            right_q += _q_block(i, row, include_exp=True)
            opts = get_options(row)
            al, at = get_answer_label(row, opts)
            ans_col.append(Paragraph(f"{i}. {circle(al)}", sAnsCol))

        # ৩ কলাম: বাম MCQ | ডান MCQ | উত্তর তালিকা
        ans_col_w = 2.0 * cm
        q_col_w   = (FULL_W - ans_col_w - COL_GAP * 2) / 2
        tbl = Table(
            [[left_q, right_q, ans_col]],
            colWidths=[q_col_w, q_col_w, ans_col_w]
        )
        tbl.setStyle(TableStyle([
            ("VALIGN",      (0,0),(-1,-1), "TOP"),
            ("LINEAFTER",   (0,0),(0,-1),  0.5, C_LINE),
            ("LINEAFTER",   (1,0),(1,-1),  0.5, C_LINE),
            ("LEFTPADDING", (0,0),(-1,-1), 2),
            ("RIGHTPADDING",(0,0),(-1,-1), 6),
            ("TOPPADDING",  (0,0),(-1,-1), 0),
            ("BOTTOMPADDING",(0,0),(-1,-1), 0),
        ]))
        story.append(tbl)

    return story

# ─── FORMAT 2 ────────────────────────────────────────────
# উত্তর MCQ এর নিচে, ব্যাখ্যা বক্সে
def _build_format_2(rows, topic, qpp):
    import math
    story = _page_header(topic)
    pages = [rows[i:i+qpp] for i in range(0, len(rows), qpp)]

    for p_idx, page in enumerate(pages):
        if p_idx > 0:
            story.append(PageBreak())

        n    = len(page)
        half = math.ceil(n / 2)
        left_rows  = page[:half]
        right_rows = page[half:]

        q_start = p_idx * qpp + 1
        left_q  = []
        for i, row in enumerate(left_rows, q_start):
            left_q += _q_block(i, row, include_ans=True, include_exp=True)

        rstart = q_start + half
        right_q = []
        for i, row in enumerate(right_rows, rstart):
            right_q += _q_block(i, row, include_ans=True, include_exp=True)

        tbl = Table([[left_q, right_q]], colWidths=[COL_W, COL_W])
        tbl.setStyle(TableStyle([
            ("VALIGN",  (0,0),(-1,-1), "TOP"),
            ("LINEAFTER",(0,0),(0,-1), 0.5, C_LINE),
            ("LEFTPADDING",(0,0),(-1,-1), 2),
            ("RIGHTPADDING",(0,0),(-1,-1), 6),
            ("TOPPADDING",(0,0),(-1,-1), 0),
            ("BOTTOMPADDING",(0,0),(-1,-1), 0),
        ]))
        story.append(tbl)

    return story

# ─── FORMAT 3 ────────────────────────────────────────────
# পেইজের একদম নিচে Answer+ব্যাখ্যা ছকে
def _build_format_3(rows, topic, qpp):
    import math
    story = _page_header(topic)
    sT    = S("T3", size=8, bold=True, color=C_HEADER)
    sCell = S("TC", size=7.5)
    pages = [rows[i:i+qpp] for i in range(0, len(rows), qpp)]

    for p_idx, page in enumerate(pages):
        if p_idx > 0:
            story.append(PageBreak())

        n    = len(page)
        half = math.ceil(n / 2)
        q_start = p_idx * qpp + 1

        left_q  = []
        for i, row in enumerate(page[:half], q_start):
            left_q += _q_block(i, row)

        rstart  = q_start + half
        right_q = []
        for i, row in enumerate(page[half:], rstart):
            right_q += _q_block(i, row)

        tbl = Table([[left_q, right_q]], colWidths=[COL_W, COL_W])
        tbl.setStyle(TableStyle([
            ("VALIGN",  (0,0),(-1,-1), "TOP"),
            ("LINEAFTER",(0,0),(0,-1), 0.5, C_LINE),
            ("LEFTPADDING",(0,0),(-1,-1), 2),
            ("RIGHTPADDING",(0,0),(-1,-1), 6),
            ("TOPPADDING",(0,0),(-1,-1), 0),
            ("BOTTOMPADDING",(0,0),(-1,-1), 0),
        ]))
        story.append(tbl)
        story.append(Spacer(1, 8))
        story.append(_divider())

        # উত্তর + ব্যাখ্যা ছক
        table_data  = [[
            Paragraph("<b>প্রশ্ন নং</b>", sT),
            Paragraph("<b>উত্তর</b>",     sT),
            Paragraph("<b>ব্যাখ্যা</b>",  sT),
        ]]
        for i, row in enumerate(page, q_start):
            opts = get_options(row)
            al, at = get_answer_label(row, opts)
            exp    = row.get("explanation","").strip()
            table_data.append([
                Paragraph(str(i), sCell),
                Paragraph(circle(al), sCell),
                Paragraph(exp, sCell),
            ])
        ans_tbl = Table(table_data, colWidths=[1.2*cm, 1.5*cm, FULL_W-2.7*cm])
        ans_tbl.setStyle(TableStyle([
            ("BACKGROUND", (0,0),(-1,0),   C_HEADER),
            ("TEXTCOLOR",  (0,0),(-1,0),   C_WHITE),
            ("BACKGROUND", (0,1),(-1,-1),  C_ANS),
            ("ROWBACKGROUNDS",(0,1),(-1,-1),[C_WHITE, C_ANS]),
            ("BOX",        (0,0),(-1,-1),  0.5, C_LINE),
            ("INNERGRID",  (0,0),(-1,-1),  0.3, C_LINE),
            ("TOPPADDING",    (0,0),(-1,-1), 3),
            ("BOTTOMPADDING", (0,0),(-1,-1), 3),
            ("LEFTPADDING",   (0,0),(-1,-1), 5),
            ("FONTNAME",   (0,0),(-1,-1), get_font(False)),
            ("FONTSIZE",   (0,0),(-1,-1), 7.5),
        ]))
        story.append(ans_tbl)

    return story

# ─── FORMAT 4 ────────────────────────────────────────────
# MCQ এর নিচে ব্যাখ্যা, ডানে উত্তর কলাম
def _build_format_4(rows, topic, qpp):
    import math
    story   = _page_header(topic)
    sAH     = S("A4H", size=8, bold=True, color=C_HEADER)
    sAR     = S("A4R", size=8, bold=True, color=C_GREEN)
    pages   = [rows[i:i+qpp] for i in range(0, len(rows), qpp)]

    for p_idx, page in enumerate(pages):
        if p_idx > 0:
            story.append(PageBreak())

        n     = len(page)
        half  = math.ceil(n / 2)
        q_start = p_idx * qpp + 1

        # বাম কলাম MCQ+Exp
        left_q = []
        for i, row in enumerate(page[:half], q_start):
            left_q += _q_block(i, row, include_exp=True)

        rstart = q_start + half
        right_q = []
        for i, row in enumerate(page[half:], rstart):
            right_q += _q_block(i, row, include_exp=True)

        # উত্তর সাইড-কলাম
        ans_items = [Paragraph("<b>উত্তর</b>", sAH), Spacer(1,4)]
        for i, row in enumerate(page, q_start):
            opts = get_options(row)
            al, _ = get_answer_label(row, opts)
            ans_items.append(Paragraph(f"{i}. {circle(al)}", sAR))

        ans_w  = 1.8 * cm
        q_col  = (FULL_W - ans_w - COL_GAP * 2) / 2
        tbl = Table([[left_q, right_q, ans_items]],
                    colWidths=[q_col, q_col, ans_w])
        tbl.setStyle(TableStyle([
            ("VALIGN",  (0,0),(-1,-1), "TOP"),
            ("LINEAFTER",(0,0),(0,-1), 0.5, C_LINE),
            ("LINEAFTER",(1,0),(1,-1), 0.5, C_LINE),
            ("BACKGROUND",(2,0),(-1,-1), C_ANS),
            ("LEFTPADDING",(0,0),(-1,-1), 2),
            ("RIGHTPADDING",(0,0),(-1,-1), 5),
            ("TOPPADDING",(0,0),(-1,-1), 0),
            ("BOTTOMPADDING",(0,0),(-1,-1), 0),
        ]))
        story.append(tbl)

    return story

# ─── FORMAT 5 ────────────────────────────────────────────
# সব MCQ, তারপর লম্বা বক্সে Q.No+Answer+ব্যাখ্যা
def _build_format_5(rows, topic, qpp):
    import math
    story   = _page_header(topic)
    sAH     = S("A5H", size=9, bold=True, color=C_WHITE)
    sAR     = S("A5R", size=8)
    sAns5   = S("A5A", size=8, bold=True, color=C_BLUE)
    pages   = [rows[i:i+qpp] for i in range(0, len(rows), qpp)]

    for p_idx, page in enumerate(pages):
        if p_idx > 0:
            story.append(PageBreak())

        n     = len(page)
        half  = math.ceil(n / 2)
        q_start = p_idx * qpp + 1

        left_q = []
        for i, row in enumerate(page[:half], q_start):
            left_q += _q_block(i, row)

        rstart = q_start + half
        right_q = []
        for i, row in enumerate(page[half:], rstart):
            right_q += _q_block(i, row)

        tbl = Table([[left_q, right_q]], colWidths=[COL_W, COL_W])
        tbl.setStyle(TableStyle([
            ("VALIGN",(0,0),(-1,-1),"TOP"),
            ("LINEAFTER",(0,0),(0,-1),0.5,C_LINE),
            ("LEFTPADDING",(0,0),(-1,-1),2),
            ("RIGHTPADDING",(0,0),(-1,-1),6),
            ("TOPPADDING",(0,0),(-1,-1),0),
            ("BOTTOMPADDING",(0,0),(-1,-1),0),
        ]))
        story.append(tbl)
        story.append(Spacer(1,10))
        story.append(_divider())

        # লম্বা বক্স
        exp_data = [[
            Paragraph("<b>নং</b>",      sAH),
            Paragraph("<b>উত্তর</b>",   sAH),
            Paragraph("<b>ব্যাখ্যা</b>",sAH),
        ]]
        for i, row in enumerate(page, q_start):
            opts = get_options(row)
            al, at = get_answer_label(row, opts)
            exp    = row.get("explanation","").strip()
            exp_data.append([
                Paragraph(str(i), sAR),
                Paragraph(f"{circle(al)} {at}", sAns5),
                Paragraph(exp, sAR),
            ])
        exp_tbl = Table(exp_data, colWidths=[1.0*cm, 2.5*cm, FULL_W-3.5*cm])
        exp_tbl.setStyle(TableStyle([
            ("BACKGROUND",    (0,0),(-1,0),  C_HEADER),
            ("ROWBACKGROUNDS",(0,1),(-1,-1), [C_WHITE, C_BOX]),
            ("BOX",           (0,0),(-1,-1), 0.6, C_HEADER),
            ("INNERGRID",     (0,0),(-1,-1), 0.3, C_LINE),
            ("TOPPADDING",    (0,0),(-1,-1), 4),
            ("BOTTOMPADDING", (0,0),(-1,-1), 4),
            ("LEFTPADDING",   (0,0),(-1,-1), 5),
            ("FONTNAME",      (0,0),(-1,-1), get_font(False)),
            ("FONTSIZE",      (0,0),(-1,-1), 8),
            ("VALIGN",        (0,0),(-1,-1), "TOP"),
        ]))
        story.append(exp_tbl)

    return story

# ─── FORMAT REGISTRY ─────────────────────────────────────
# নতুন ফরম্যাট এড করতে এখানে এড করো
FORMAT_BUILDERS = {
    1: _build_format_1,
    2: _build_format_2,
    3: _build_format_3,
    4: _build_format_4,
    5: _build_format_5,
    # 6: _build_format_6,  ← নতুন ফরম্যাট এড করো এভাবে
}

# ─── PUBLIC API ───────────────────────────────────────────
import math  # global math import for sub-functions

def build_pdf(rows: list, fmt: int, topic: str = "Practice Sheet",
              qpp: int = 10) -> bytes:
    """
    PDF বাইট রিটার্ন করে।
    rows : CSV row list
    fmt  : 1–5 (ফরম্যাট নম্বর)
    topic: শিরোনাম
    qpp  : প্রতি পেইজে প্রশ্ন সংখ্যা
    """
    builder = FORMAT_BUILDERS.get(fmt, _build_format_2)
    story   = builder(rows, topic, qpp)

    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize     = A4,
        leftMargin   = MARGIN,
        rightMargin  = MARGIN,
        topMargin    = MARGIN + 0.3*cm,
        bottomMargin = MARGIN + 0.5*cm,
    )
    doc.build(story, canvasmaker=_PageNumCanvas)
    return buf.getvalue()
