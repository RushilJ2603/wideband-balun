"""Builds reference.docx, the style template pandoc uses for the report:
Times New Roman, 12 pt body text, 1.15 line spacing, one-inch margins,
dark headings and captions in italics."""

import sys

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt, Inches, RGBColor

src, out = sys.argv[1], sys.argv[2]
d = Document(src)
for s in d.sections:
    s.left_margin = s.right_margin = s.top_margin = s.bottom_margin = Inches(1)

ink = RGBColor(0x1A, 0x1A, 0x1A)
for name in ("Normal", "Body Text", "First Paragraph", "Compact"):
    if name in [x.name for x in d.styles]:
        st = d.styles[name]
        st.font.name = "Times New Roman"
        st.font.size = Pt(12)
        st.paragraph_format.line_spacing = 1.15
        st.paragraph_format.space_after = Pt(6)
for name in ("Body Text", "First Paragraph"):
    d.styles[name].paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
for name, size in (("Title", 20), ("Subtitle", 14), ("Heading 1", 15), ("Heading 2", 13), ("Heading 3", 12)):
    st = d.styles[name]
    st.font.name = "Times New Roman"
    st.font.size = Pt(size)
    st.font.bold = True
    st.font.italic = False
    st.font.color.rgb = ink
    st.paragraph_format.space_before = Pt(12)
    st.paragraph_format.space_after = Pt(6)
for name in ("Caption", "Image Caption", "Table Caption"):
    if name in [x.name for x in d.styles]:
        st = d.styles[name]
        st.font.name = "Times New Roman"
        st.font.size = Pt(10.5)
        st.font.italic = True
        st.font.color.rgb = ink
        st.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
for name in ("Author", "Date", "Abstract"):
    if name in [x.name for x in d.styles]:
        st = d.styles[name]
        st.font.name = "Times New Roman"
        st.font.color.rgb = ink
# Remove theme font references so the fonts set above apply, and add the
# styles Word uses for the table of contents with tight spacing.
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml.ns import qn

for st in d.styles:
    rpr = st.element.rPr
    if rpr is not None and rpr.rFonts is not None:
        for a in ("w:asciiTheme", "w:hAnsiTheme", "w:eastAsiaTheme", "w:cstheme"):
            if rpr.rFonts.get(qn(a)) is not None:
                del rpr.rFonts.attrib[qn(a)]
        rpr.rFonts.set(qn("w:ascii"), "Times New Roman")
        rpr.rFonts.set(qn("w:hAnsi"), "Times New Roman")
names = [x.name for x in d.styles]
for lvl, indent in ((1, 0), (2, 0.25)):
    name = f"toc {lvl}"
    st = d.styles[name] if name in names else d.styles.add_style(name, WD_STYLE_TYPE.PARAGRAPH)
    st.element.set(qn("w:styleId"), f"TOC{lvl}")
    st.base_style = d.styles["Normal"]
    st.font.name = "Times New Roman"
    st.font.size = Pt(11)
    st.paragraph_format.space_before = Pt(0)
    st.paragraph_format.space_after = Pt(2)
    st.paragraph_format.line_spacing = 1.0
    st.paragraph_format.left_indent = Inches(indent)
d.save(out)
