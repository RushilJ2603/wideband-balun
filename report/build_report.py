"""Builds report.docx from report.md with pandoc and reference.docx, then
numbers the figures, lays out the title page and adds page numbers.

    python3 build_report.py            (needs pandoc and python-docx)
"""

import re
import shutil
import subprocess
from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt

HERE = Path(__file__).resolve().parent
PANDOC = shutil.which("pandoc") or str(Path.home() / ".local/bin/pandoc")
UNNUMBERED = ("Abstract", "References", "Appendix: project files")


def preprocess(text):
    n = 0

    def fig(m):
        nonlocal n
        n += 1
        return f"![Figure {n}. {m.group(1)}]({m.group(2)})"

    text = re.sub(r"!\[(.+?)\]\((.+?)\)", fig, text, flags=re.S)
    for h in UNNUMBERED:
        cls = ".unnumbered" if h == "References" else ".unnumbered .unlisted"
        text = text.replace(f"\n# {h}\n", f"\n# {h} {{{cls}}}\n")
    return text


def page_number_field(par):
    run = par.add_run()
    for tag, text in (("begin", None), (None, "PAGE"), ("end", None)):
        if tag:
            el = OxmlElement("w:fldChar")
            el.set(qn("w:fldCharType"), tag)
        else:
            el = OxmlElement("w:instrText")
            el.set(qn("xml:space"), "preserve")
            el.text = text
        run._r.append(el)


def postprocess(path):
    d = Document(path)
    body = d.paragraphs
    styles = [p.style.name for p in body]
    # Title block: title, subtitle, authors and date, centred, with space
    # above, and a page break after the date.
    last = max(i for i, s in enumerate(styles[:8]) if s in ("Title", "Subtitle", "Author", "Date"))
    for p in body[: last + 1]:
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for r in p.runs:
            r.font.name = "Times New Roman"
            if p.style.name == "Author":
                r.font.size = Pt(13)
            if p.style.name == "Date":
                r.font.size = Pt(12)
    body[0].paragraph_format.space_before = Pt(170)
    date = body[last]
    for text in ("Department of Electronics and Communication Engineering",
                 "National Institute of Technology Karnataka, Surathkal"):
        p = date.insert_paragraph_before(text, style=date.style)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    date.paragraph_format.space_before = Pt(24)
    date.runs[-1].add_break(WD_BREAK.PAGE)
    # Abstract and appendix keep the look of a heading but stay out of the
    # table of contents, which Word builds from the heading styles.
    from docx.enum.style import WD_STYLE_TYPE
    st = d.styles.add_style("Plain Heading", WD_STYLE_TYPE.PARAGRAPH)
    st.base_style = d.styles["Normal"]
    st.font.name = "Times New Roman"
    st.font.size = Pt(15)
    st.font.bold = True
    st.paragraph_format.space_before = Pt(12)
    st.paragraph_format.space_after = Pt(6)
    st.paragraph_format.keep_with_next = True
    for p in body:
        if p.style.name == "Heading 1" and p.text.strip() in ("Abstract", "Appendix: project files"):
            p.style = st
    # Page break after the table of contents.
    for p in body:
        if p.text.strip() == "Abstract":
            p.paragraph_format.page_break_before = True
        if p.style.name == "Heading 1" and p.text.strip().startswith("Introduction"):
            p.paragraph_format.page_break_before = True
    # Keep each table on one page together with its caption.
    for p in body:
        if p.style.name == "Table Caption":
            p.paragraph_format.keep_with_next = True
    for t in d.tables:
        t.style = d.styles["Table"] if "Table" in [s.name for s in d.styles] else t.style
        t.alignment = 1
        for k, row in enumerate(t.rows):
            for cell in row.cells:
                for p in cell.paragraphs:
                    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                    p.paragraph_format.space_after = Pt(2)
                    p.paragraph_format.keep_with_next = k < len(t.rows) - 1
                    for r in p.runs:
                        r.font.size = Pt(10)
    footer = d.sections[0].footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    page_number_field(footer)
    d.save(path)


def main():
    src = preprocess((HERE / "report.md").read_text(encoding="utf-8"))
    tmp = HERE / "_build.md"
    tmp.write_text(src, encoding="utf-8")
    out = HERE / "Wideband_Balun_Report.docx"
    subprocess.run([PANDOC, str(tmp), "-o", str(out), "--reference-doc", str(HERE / "reference.docx"),
                    "--number-sections", "--toc", "--toc-depth=2", "--resource-path", str(HERE),
                    "-M", "toc-title=Contents"], check=True, cwd=HERE)
    tmp.unlink()
    postprocess(out)
    print("wrote", out.name)


if __name__ == "__main__":
    main()
