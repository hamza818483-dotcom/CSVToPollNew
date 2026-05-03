# ============================================================
#  utils/csv_helper.py  —  CSV পার্স + অপশন হেল্পার
# ============================================================

import csv
import io

OPTION_LABELS = ["A", "B", "C", "D", "E"]
CIRCLE = {"A": "Ⓐ", "B": "Ⓑ", "C": "Ⓒ", "D": "Ⓓ", "E": "Ⓔ"}

def parse_csv_bytes(data: bytes):
    text = data.decode("utf-8-sig", errors="replace")
    reader = csv.DictReader(io.StringIO(text))
    rows = list(reader)
    headers = list(reader.fieldnames or [])
    return rows, headers

def get_options(row: dict) -> list:
    """row থেকে option1-5 বের করে।"""
    opts = []
    for i in range(1, 6):
        for key in [f"option{i}", f"option({i})", f"option_{i}"]:
            val = row.get(key, "").strip()
            if val:
                opts.append(val)
                break
    return opts

def get_answer_label(row: dict, opts: list):
    """
    Returns (label, text) — e.g. ("B", "কুইনাইন")
    answer কলামে 1-based index থাকবে।
    """
    try:
        idx = int(row.get("answer", "1")) - 1
        if 0 <= idx < len(opts):
            return OPTION_LABELS[idx], opts[idx]
    except Exception:
        pass
    return "A", (opts[0] if opts else "?")

def circle(label: str) -> str:
    return CIRCLE.get(label.upper(), label)
