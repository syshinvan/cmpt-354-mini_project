"""
Builds mp.pdf (Steps 1-3, per the submission instructions) from the existing
markdown writeups and rendered ER diagrams. Run after Step2's ERD scripts.
"""
import os
import re
import sys
from fpdf import FPDF

HERE = os.path.dirname(os.path.abspath(__file__))


def find_font_dir():
    """Locate a directory holding the DejaVu .ttf fonts: matplotlib's bundled
    mpl-data/fonts/ttf first, then the usual system font directories."""
    needed = ["DejaVuSans.ttf", "DejaVuSans-Bold.ttf",
              "DejaVuSans-Oblique.ttf", "DejaVuSansMono.ttf"]
    dirs = []
    try:
        import matplotlib
        dirs.append(os.path.join(matplotlib.get_data_path(), "fonts", "ttf"))
    except ImportError:
        pass
    dirs += ["/System/Library/Fonts", "/System/Library/Fonts/Supplemental",
             "/Library/Fonts", os.path.expanduser("~/Library/Fonts"),
             "/usr/share/fonts", "/usr/local/share/fonts"]
    for d in dirs:
        if all(os.path.isfile(os.path.join(d, f)) for f in needed):
            return d
    for d in dirs:  # system font dirs often nest fonts in subdirectories
        for root, _subdirs, files in os.walk(d):
            if all(f in files for f in needed):
                return root
    sys.exit("error: DejaVu .ttf fonts not found in matplotlib's mpl-data or "
             "the system font directories searched: " + ", ".join(dirs))


FONT_DIR = find_font_dir()

pdf = FPDF()
pdf.add_font("DejaVu", "", os.path.join(FONT_DIR, "DejaVuSans.ttf"))
pdf.add_font("DejaVu", "B", os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf"))
pdf.add_font("DejaVu", "I", os.path.join(FONT_DIR, "DejaVuSans-Oblique.ttf"))
pdf.add_font("DejaVuMono", "", os.path.join(FONT_DIR, "DejaVuSansMono.ttf"))
pdf.set_auto_page_break(auto=True, margin=18)
pdf.set_margins(18, 18, 18)


def clean(text):
    # Protect `code span` contents from the italic pass below: a stray * inside a
    # code span (e.g. `*_Disjoint`) would otherwise pair up with an unrelated *
    # elsewhere in the line and italicize everything in between.
    code_spans = []

    def stash(m):
        code_spans.append(m.group(1))
        return f"\x00{len(code_spans) - 1}\x00"

    text = re.sub(r"`([^`]*)`", stash, text)
    # fpdf2's markdown mode only understands **bold** and __italic__; convert
    # lone *italic* markers (not part of a **bold** pair) to that form.
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"__\1__", text)
    for i, span in enumerate(code_spans):
        text = text.replace(f"\x00{i}\x00", span)
    return text


def section_break():
    pdf.add_page()
    pdf.set_font("DejaVu", "B", 18)
    pdf.ln(4)


def render_markdown(md_path, skip_first_title=True):
    with open(md_path, encoding="utf-8") as f:
        lines = f.read().split("\n")
    skipped = not skip_first_title
    buf = []
    buf_is_bullet = False
    in_code = False

    def flush():
        nonlocal buf, buf_is_bullet
        if not buf:
            buf_is_bullet = False
            return
        text = " ".join(buf)
        buf = []
        pdf.set_font("DejaVu", "", 9.7)
        if buf_is_bullet:
            pdf.set_x(pdf.l_margin + 4)
            pdf.multi_cell(pdf.w - pdf.r_margin - pdf.l_margin - 4, 5.6,
                            clean("•  " + text), markdown=True, align="L",
                            new_x="LMARGIN", new_y="NEXT")
        else:
            pdf.set_x(pdf.l_margin)
            pdf.multi_cell(0, 5.6, clean(text), markdown=True, align="L",
                            new_x="LMARGIN", new_y="NEXT")
        buf_is_bullet = False

    for raw in lines:
        stripped = raw.rstrip().strip()

        if stripped.startswith("```"):
            flush()
            in_code = not in_code
            if in_code:
                pdf.ln(1)
            else:
                pdf.ln(2)
            continue

        if in_code:
            pdf.set_font("DejaVuMono", "", 7.8)
            pdf.set_x(pdf.l_margin + 4)
            pdf.multi_cell(pdf.w - pdf.r_margin - pdf.l_margin - 4, 5, stripped,
                            align="L", new_x="LMARGIN", new_y="NEXT")
            continue

        if raw.startswith("# "):
            flush()
            if not skipped:
                skipped = True
                continue
            pdf.set_font("DejaVu", "B", 15)
            pdf.set_x(pdf.l_margin)
            pdf.multi_cell(0, 8, clean(stripped[2:]), markdown=True, align="L", new_x="LMARGIN", new_y="NEXT")
            pdf.ln(1)
        elif raw.startswith("## "):
            flush()
            pdf.set_font("DejaVu", "B", 12.5)
            pdf.ln(1)
            pdf.set_x(pdf.l_margin)
            pdf.multi_cell(0, 7.5, clean(stripped[3:]), markdown=True, align="L", new_x="LMARGIN", new_y="NEXT")
            pdf.ln(0.5)
        elif stripped == "---":
            flush()
            pdf.ln(1.5)
            y = pdf.get_y()
            pdf.line(pdf.l_margin, y, pdf.w - pdf.r_margin, y)
            pdf.ln(3)
        elif stripped == "":
            flush()
            pdf.ln(2.5)
        elif re.match(r"^\d+\.\s", stripped) or stripped.startswith("- "):
            flush()
            buf_is_bullet = True
            buf.append(re.sub(r"^-\s|^\d+\.\s", "", stripped))
        else:
            buf.append(stripped)
    flush()


# ---------- Title page ----------
pdf.add_page()
pdf.ln(70)
pdf.set_font("DejaVu", "B", 24)
pdf.cell(0, 12, "CMPT 354 Mini Project", align="C", new_x="LMARGIN", new_y="NEXT")
pdf.cell(0, 12, "Library Database", align="C", new_x="LMARGIN", new_y="NEXT")
pdf.set_font("DejaVu", "", 13)
pdf.ln(8)
pdf.cell(0, 8, "Steps 1-3: Project Specifications, E/R Diagrams, BCNF Analysis", align="C", new_x="LMARGIN", new_y="NEXT")
pdf.ln(4)
pdf.set_font("DejaVu", "I", 11)
pdf.cell(0, 8, "Person A: Item / Loan / Fine / AcquisitionCandidate", align="C", new_x="LMARGIN", new_y="NEXT")
pdf.cell(0, 8, "Person B: Person / Room / Event / AudienceGroup", align="C", new_x="LMARGIN", new_y="NEXT")

# ---------- Step 1 ----------
section_break()
pdf.multi_cell(0, 8, "Step 1: Project Specifications", markdown=False)
pdf.ln(2)
pdf.set_font("DejaVu", "", 9.7)
pdf.multi_cell(
    0, 5.6,
    "The library holds print books, online books, magazines, scientific journals, and "
    "recordings; people can borrow and return items and may be fined for late returns; the "
    "library also holds events (book clubs, art shows, film screenings, and others) recommended "
    "for specific audiences and held in library rooms, which people can attend for free; the "
    "library keeps personnel records and tracks candidate items for future acquisition. The rest "
    "of the domain is specified below, split by the two halves of the schema.",
    align="L",
)
pdf.ln(3)
render_markdown(os.path.join(HERE, "Step1_PersonA_Spec.md"))
pdf.ln(4)
render_markdown(os.path.join(HERE, "Step1_PersonB_Spec.md"))

# ---------- Step 2 ----------
section_break()
pdf.multi_cell(0, 8, "Step 2: E/R Diagrams", markdown=False)
pdf.ln(2)
pdf.set_font("DejaVu", "", 9.7)
pdf.multi_cell(
    0, 5.6,
    "Notation: rectangle = entity set, double rectangle = weak entity set, oval = attribute "
    "(solid underline = key, dashed underline = partial key), diamond = relationship, double "
    "diamond = identifying relationship, double line = total participation, triangle = isa. "
    "Dashed boxes are placeholders marking "
    "where a relationship crosses into the other half's diagram (captioned accordingly); the two "
    "halves share identical relationship names (DonatedBy, By, Suggested) at every crossing point.",
    align="L",
)

for img in ("Step2_PersonA_ERD.png", "Step2_PersonB_ERD.png"):
    pdf.add_page(orientation="L")
    path = os.path.join(HERE, img)
    pdf.image(path, x=10, y=10, w=pdf.w - 20)

# ---------- Step 3 ----------
section_break()
pdf.multi_cell(0, 8, "Step 3: Does Your Design Allow Anomalies?", markdown=False)
pdf.ln(2)
render_markdown(os.path.join(HERE, "Step3_PersonA_BCNF.md"))
pdf.ln(4)
render_markdown(os.path.join(HERE, "Step3_PersonB_BCNF.md"))

out = os.path.join(HERE, "mp.pdf")
pdf.output(out)
print("saved:", out)
