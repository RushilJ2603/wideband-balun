"""Builds Balun_quick_sheet.pdf in the project folder from quick_sheet.md:
pandoc writes a .docx with reference.docx, the tables get borders and a
smaller font, and Word writes the PDF (export_pdf.ps1).

    python3 build_quick_sheet.py      (WSL, needs pandoc, python-docx, Word)
"""

import shutil
import subprocess
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt

HERE = Path(__file__).resolve().parent
PANDOC = shutil.which("pandoc") or str(Path.home() / ".local/bin/pandoc")


def win_temp():
    t = subprocess.check_output(["cmd.exe", "/c", "echo %TEMP%"], text=True, stderr=subprocess.DEVNULL).strip()
    return Path(subprocess.check_output(["wslpath", t], text=True).strip())


def borders(table):
    tbl_pr = table._tbl.tblPr
    b = OxmlElement("w:tblBorders")
    for side in ("top", "left", "bottom", "right", "insideH", "insideV"):
        e = OxmlElement(f"w:{side}")
        e.set(qn("w:val"), "single")
        e.set(qn("w:sz"), "4")
        e.set(qn("w:color"), "000000")
        b.append(e)
    tbl_pr.append(b)


def tidy(path):
    d = Document(path)
    for s in d.sections:
        s.left_margin = s.right_margin = Cm(1.8)
        s.top_margin = s.bottom_margin = Cm(1.6)
    d.styles["Compact"].font.size = Pt(9)
    for t in d.tables:
        borders(t)
        for k, row in enumerate(t.rows):
            row._tr.get_or_add_trPr().append(OxmlElement("w:cantSplit"))
            for cell in row.cells:
                for p in cell.paragraphs:
                    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                    p.paragraph_format.space_before = Pt(1)
                    p.paragraph_format.space_after = Pt(1)
                    for r in p.runs:
                        r.font.size = Pt(9)
                        if k == 0:
                            r.font.bold = True
    d.save(path)


def main():
    tmp = win_temp()
    docx = tmp / "Balun_quick_sheet.docx"
    subprocess.run([PANDOC, str(HERE / "quick_sheet.md"), "-o", str(docx),
                    "--reference-doc", str(HERE / "reference.docx")], check=True)
    tidy(docx)
    win = subprocess.check_output(["wslpath", "-w", str(docx)], text=True).strip()
    ps1 = subprocess.check_output(["wslpath", "-w", str(HERE / "export_pdf.ps1")], text=True).strip()
    subprocess.run(["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", ps1, win], check=True)
    out = HERE.parent / "Balun_quick_sheet.pdf"
    shutil.copyfile(docx.with_suffix(".pdf"), out)
    print("wrote", out)


if __name__ == "__main__":
    main()
