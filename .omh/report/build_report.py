#!/usr/bin/env python3
"""Build the Cloud Analytics activity report PDF for Devyansh's portfolio project.
Mirrors the structure of the reference report (DHRUVI_BAGGA.pdf):
cover page + 16 numbered sections, with tables (wrapped cells) and vector
flow diagrams rendered with reportlab graphics.
"""
import os
from xml.sax.saxutils import escape
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate, Frame, PageTemplate, Paragraph, Spacer, Table, TableStyle,
    Image, PageBreak, NextPageTemplate,
)
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.graphics.shapes import Drawing, Rect, String, Line, Polygon

OUT = r"C:\Users\Admin\Downloads\DEVYANSH_GUPTA.pdf"
IMG = r"C:\Users\Admin\Documents\Projects\portfolio\.omh\report"

# ---------- fonts (TrueType so bullets/arrows render correctly) ----------
pdfmetrics.registerFont(TTFont("Arial", "C:/Windows/Fonts/arial.ttf"))
pdfmetrics.registerFont(TTFont("Arial-Bold", "C:/Windows/Fonts/arialbd.ttf"))
pdfmetrics.registerFont(TTFont("Arial-Oblique", "C:/Windows/Fonts/ariali.ttf"))
pdfmetrics.registerFontFamily("Arial", normal="Arial", bold="Arial-Bold",
                              italic="Arial-Oblique", boldItalic="Arial-Bold")

# ---------- styles ----------
def st(name, **kw):
    return ParagraphStyle(name, **kw)

cover_title  = st("ct", fontName="Arial-Bold", fontSize=16, leading=22, alignment=TA_CENTER)
cover_big   = st("cb", fontName="Arial-Bold", fontSize=20, leading=26, alignment=TA_CENTER)
cover_norm  = st("cn", fontName="Arial", fontSize=13, leading=20, alignment=TA_CENTER)
h1  = st("h1", fontName="Arial-Bold", fontSize=13.5, leading=17, spaceBefore=14, spaceAfter=6)
h2  = st("h2", fontName="Arial-Bold", fontSize=11.5, leading=15, spaceBefore=10, spaceAfter=4)
body = st("body", fontName="Arial", fontSize=10.5, leading=15, alignment=TA_JUSTIFY, spaceAfter=5)
bullet = st("bullet", fontName="Arial", fontSize=10.5, leading=15, leftIndent=16, spaceAfter=2)
flow = st("flow", fontName="Courier-Bold", fontSize=10.5, leading=16, alignment=TA_CENTER, spaceAfter=2)
caption = st("cap", fontName="Arial-Oblique", fontSize=9, leading=12, alignment=TA_CENTER,
             textColor=colors.grey, spaceBefore=2, spaceAfter=10)
cell_s  = st("cell", fontName="Arial", fontSize=9, leading=11.5)
cellb_s = st("cellb", fontName="Arial-Bold", fontSize=9, leading=11.5)

def P(text, style=body): return Paragraph(text, style)
def B(text): return Paragraph("&bull;&nbsp;&nbsp;" + text, bullet)
def NB(n, text): return Paragraph(f"<b>{n}.</b>&nbsp;&nbsp;{text}", bullet)

# ---------- tables: every cell wrapped in a Paragraph so text WRAPS ----------
def tbl(rows, widths=None, header=True, fs=9):
    cs  = ParagraphStyle("c", parent=cell_s, fontSize=fs, leading=fs + 2.5)
    cbs = ParagraphStyle("cb", parent=cellb_s, fontSize=fs, leading=fs + 2.5)
    wrapped = []
    for r_i, row in enumerate(rows):
        out = []
        for c in row:
            s = cbs if (header and r_i == 0) else cs
            out.append(Paragraph(escape(str(c)), s))
        wrapped.append(out)
    t = Table(wrapped, colWidths=widths, repeatRows=1 if header else 0)
    style = [
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]
    if header:
        style += [("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e8e8e8"))]
    t.setStyle(TableStyle(style))
    return t

# ---------- vector flow diagrams ----------
INK  = colors.HexColor("#1A1A1A")
EDGE = colors.HexColor("#2C3E50")
FILL = colors.HexColor("#EDF2F7")
GFILL, GEDGE = colors.HexColor("#E6F4EA"), colors.HexColor("#1E7E34")
WFILL, WEDGE = colors.HexColor("#FFF4E5"), colors.HexColor("#B26B00")

def _fit(font, size, text, maxw):
    while size > 6 and pdfmetrics.stringWidth(text, font, size) > maxw:
        size -= 0.25
    return size

def _box(d, x, y, w, h, title, sub=None, fill=FILL, edge=EDGE):
    d.add(Rect(x, y, w, h, rx=5, ry=5, fillColor=fill, strokeColor=edge, strokeWidth=1.1))
    if sub:
        tf = _fit("Arial-Bold", 9.5, title, w - 10)
        sf = _fit("Arial", 8, sub, w - 10)
        d.add(String(x + w / 2, y + h - 15, title, fontName="Arial-Bold", fontSize=tf,
                     textAnchor="middle", fillColor=INK))
        d.add(String(x + w / 2, y + 7, sub, fontName="Arial", fontSize=sf,
                     textAnchor="middle", fillColor=colors.HexColor("#444444")))
    else:
        tf = _fit("Arial-Bold", 9.5, title, w - 10)
        d.add(String(x + w / 2, y + h / 2 - tf * 0.36, title, fontName="Arial-Bold",
                     fontSize=tf, textAnchor="middle", fillColor=INK))

def _head_down(d, x, y):
    d.add(Polygon(points=[x - 3.5, y + 8, x + 3.5, y + 8, x, y],
                  fillColor=EDGE, strokeColor=EDGE, strokeWidth=0.8))

def _head_left(d, x, y):
    d.add(Polygon(points=[x + 8, y - 3.5, x + 8, y + 3.5, x, y],
                  fillColor=EDGE, strokeColor=EDGE, strokeWidth=0.8))

def _head_right(d, x, y):
    d.add(Polygon(points=[x - 8, y - 3.5, x - 8, y + 3.5, x, y],
                  fillColor=EDGE, strokeColor=EDGE, strokeWidth=0.8))

def _varrow(d, x, y1, y2):
    d.add(Line(x, y1, x, y2 + 8, strokeColor=EDGE, strokeWidth=1.1))
    _head_down(d, x, y2)

def _harrow_r(d, x1, x2, y):
    d.add(Line(x1, y, x2 - 8, y, strokeColor=EDGE, strokeWidth=1.1))
    _head_right(d, x2, y)

def _harrow_l(d, x1, x2, y):
    d.add(Line(x1, y, x2 + 8, y, strokeColor=EDGE, strokeWidth=1.1))
    _head_left(d, x2, y)

def fig_caption(text):
    return P(text, caption)

def img_els(items):
    """items: list of (path, width, caption) -> flowable list with images + captions."""
    from reportlab.lib.utils import ImageReader
    out = []
    for path, width, cap in items:
        ir = ImageReader(path)
        w, h = ir.getSize()
        out.append(Image(path, width=width, height=width * h / w))
        if cap:
            out.append(P(cap, caption))
    return out

def flow_v(steps, width=440, box_w=300, gap=20):
    """Vertical chain of boxes with downward arrows.
    steps: list of dicts {t: title, s: sub (opt), kind: ''|'ok'|'warn'}"""
    n = len(steps)
    hs = [42 if s.get("s") else 30 for s in steps]
    H = sum(hs) + gap * (n - 1) + 10
    d = Drawing(width, H)
    y = H - 5
    cx = width / 2
    for i, s in enumerate(steps):
        h = hs[i]
        if s.get("kind") == "ok":
            fill, edge = GFILL, GEDGE
        elif s.get("kind") == "warn":
            fill, edge = WFILL, WEDGE
        else:
            fill, edge = FILL, EDGE
        _box(d, cx - box_w / 2, y - h, box_w, h, s["t"], s.get("s"), fill, edge)
        if i < n - 1:
            _varrow(d, cx, y - h - 3, y - h - gap + 3)
        y -= h + gap
    return d

def flow_branch():
    """Two-path delivery: form -> (primary | fallback) -> inbox."""
    W, H = 440, 196
    d = Drawing(W, H)
    # top box
    _box(d, 100, H - 42, 240, 34, "Contact form submitted", "name - email - message")
    # elbow: top -> both mids
    ymid_top, mids_y, mid_h, bw = H - 66, H - 112, 46, 185
    lx, rx = 25, 230
    lcx, rcx = lx + bw / 2, rx + bw / 2
    for cx in (lcx, rcx):
        d.add(Line(220, H - 42, 220, H - 54, strokeColor=EDGE, strokeWidth=1.1))
        d.add(Line(220, H - 54, cx, H - 54, strokeColor=EDGE, strokeWidth=1.1))
        d.add(Line(cx, H - 54, cx, mids_y + mid_h + 8, strokeColor=EDGE, strokeWidth=1.1))
        _head_down(d, cx, mids_y + mid_h)
    # path labels
    d.add(String(lcx, H - 52, "primary", fontName="Arial-Oblique", fontSize=7,
                 textAnchor="middle", fillColor=colors.HexColor("#555555")))
    d.add(String(rcx, H - 52, "on failure: fallback", fontName="Arial-Oblique", fontSize=7,
                 textAnchor="middle", fillColor=colors.HexColor("#555555")))
    # mid boxes
    _box(d, lx, mids_y, bw, mid_h, "Azure Function", "POST /api/contact, SMTP",
         fill=FILL, edge=EDGE)
    _box(d, rx, mids_y, bw, mid_h, "formsubmit.co", "browser AJAX, same inbox",
         fill=WFILL, edge=WEDGE)
    # mids -> bottom
    bot_y, bot_h, bbw = H - 178, 40, 250
    for cx in (lcx, rcx):
        d.add(Line(cx, mids_y, cx, mids_y - 13, strokeColor=EDGE, strokeWidth=1.1))
        d.add(Line(cx, mids_y - 13, 220, mids_y - 13, strokeColor=EDGE, strokeWidth=1.1))
        d.add(Line(220, mids_y - 13, 220, bot_y + bot_h + 8, strokeColor=EDGE, strokeWidth=1.1))
    _head_down(d, 220, bot_y + bot_h)
    _box(d, 95, bot_y, bbw, bot_h, "Personal inbox", "message delivered - no database",
         fill=GFILL, edge=GEDGE)
    return d

def flow_snake(items):
    """Two-row reading order: row 1 left->right, then down, row 2 right->left."""
    W, chip_w, chip_h, hgap = 440, 95, 28, 20
    row1_y, row2_y = 66, 0
    H = chip_h + row1_y + chip_h + 10
    d = Drawing(W, H)
    xs = [0, 115, 230, 345]
    # row 1
    for i, label in enumerate(items[:4]):
        _box(d, xs[i], row1_y, chip_w, chip_h, label)
        if i < 3:
            _harrow_r(d, xs[i] + chip_w + 2, xs[i + 1] - 2, row1_y + chip_h / 2)
    # connector row1 rightmost -> row2 rightmost
    _varrow(d, xs[3] + chip_w / 2, row1_y - 2, row2_y + chip_h + 2)
    # row 2 (right to left flow)
    for i, label in enumerate(items[4:]):
        x = xs[3 - i]
        _box(d, x, row2_y, chip_w, chip_h, label)
        if i < 3:
            _harrow_l(d, x - 2, xs[3 - i] - chip_w - 2, row2_y + chip_h / 2)
    return d

def flow_h(steps):
    """Horizontal chain: steps = [(title, sub, kind)] left to right."""
    W, bw, bh, gap = 440, 78, 44, 12.5
    d = Drawing(W, bh + 10)
    y = 5
    for i, (title, sub, kind) in enumerate(steps):
        x = i * (bw + gap)
        fill, edge = (GFILL, GEDGE) if kind == "ok" else (FILL, EDGE)
        _box(d, x, y, bw, bh, title, sub, fill, edge)
        if i < len(steps) - 1:
            _harrow_r(d, x + bw + 1, x + bw + gap - 1, y + bh / 2)
    return d

# ---------- page furniture ----------
def cover_page(canv, doc):
    canv.saveState()
    canv.setFont("Helvetica", 9)
    canv.drawCentredString(A4[0] / 2, 0.5 * inch, "Page 1")
    canv.restoreState()

def later_page(canv, doc):
    canv.saveState()
    canv.setFont("Helvetica", 9)
    canv.drawCentredString(A4[0] / 2, 0.5 * inch, f"Page {doc.page}")
    canv.restoreState()

doc = BaseDocTemplate(OUT, pagesize=A4,
                      title="Portfolio Project Report - Cloud Analytics Activity-1",
                      author="Devyansh Gupta",
                      leftMargin=62, rightMargin=62, topMargin=64, bottomMargin=58)
frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="main")
doc.addPageTemplates([
    PageTemplate(id="Cover", frames=[frame], onPage=cover_page),
    PageTemplate(id="Body", frames=[frame], onPage=later_page),
])

story = []

# ══════════════ COVER ══════════════
story += [
    Spacer(1, 46),
    P("DEPARTMENT OF CS &amp; IT", cover_title),
    P("Programme: MCA", cover_norm),
    Spacer(1, 34),
    P("Activity-1", cover_big),
    P("CLOUD ANALYTICS", cover_big),
    Spacer(1, 14),
    P("25MCASC302L", cover_norm),
    Spacer(1, 40),
    P("Name: <b>DEVYANSH GUPTA</b>&nbsp;&nbsp;&nbsp;USN: <b>25MCAR0193</b>", cover_norm),
    Spacer(1, 12),
    P("Semester: 3<super>rd</super> Semester&nbsp;&nbsp;&nbsp;Branch: MCA-SCT", cover_norm),
    Spacer(1, 34),
    P("Submitted to: Dr. PRABHAKARN, Associate Professor", cover_norm),
    P("School of CS &amp; IT", cover_norm),
    Spacer(1, 34),
    P("Academic Year: 2026-2027", cover_norm),
    NextPageTemplate("Body"),
    PageBreak(),
]

# ══════════════ 1. INTRODUCTION ══════════════
story += [
    P("1. INTRODUCTION AND OBJECTIVES", h1),
    P("1.1 Introduction", h2),
    P("The objective of this project is to design and develop a professional personal portfolio "
      "website that presents my academic background, technical skills, projects, experience, "
      "research publications, and certifications in a structured and visually appealing manner."),
    P("The portfolio has been developed as a modern web application using plain HTML, CSS, and "
      "JavaScript, animated with the anime.js v4 animation library (vendored locally, MIT "
      "licensed). It is deployed on Microsoft Azure Static Web Apps, which provides a global CDN "
      "for the static front end together with managed serverless Azure Functions for backend "
      "processing. The website includes a functional Contact form. Unlike a traditional "
      "form-plus-database design, submitted contact messages are processed by a serverless "
      "Azure Function and delivered <b>directly to my personal email inbox</b> - no database is "
      "involved at any point, so no visitor data is stored or retained anywhere."),
    P("The resume is served straight from the website as a bundled PDF asset with a native "
      "browser download. An earlier iteration of the project used Azure Blob Storage with "
      "server-minted, short-lived Shared Access Signature (SAS) links for the resume; that "
      "integration was subsequently removed and simplified to the direct-download design after "
      "live testing showed the extra storage layer added failure modes without adding value."),
    P("The complete project is maintained on GitHub, and GitHub Actions automates the build and "
      "deployment process. This demonstrates the practical use of cloud computing, serverless "
      "backend development, version control, and CI/CD concepts in a single project."),
    P("1.2 Objectives", h2),
    NB(1, "<b>Create a professional online portfolio</b> - a single platform representing my technical profile, education, experience, projects, publications, and certifications."),
    NB(2, "<b>Demonstrate technical skills</b> - cloud computing, DevOps, backend development, security, and related technologies."),
    NB(3, "<b>Develop a responsive frontend</b> - an interactive, animated interface built with plain HTML/CSS/JS (no framework build step) that adapts to different screen sizes."),
    NB(4, "<b>Implement serverless backend functionality</b> - an Azure Function that validates and processes contact form submissions."),
    NB(5, "<b>Deliver contact messages straight to email</b> - route form submissions to my personal inbox with no database layer, including an automatic fallback delivery path."),
    NB(6, "<b>Serve the resume directly from the site</b> - a reliable, one-click resume download that requires no external storage service."),
    NB(7, "<b>Use cloud deployment</b> - host the portfolio on Azure Static Web Apps, accessible through a public URL."),
    NB(8, "<b>Implement CI/CD</b> - automate build and deployment with GitHub Actions on every push to the repository."),
    NB(9, "<b>Demonstrate an end-to-end cloud architecture</b> - connect the frontend, serverless API, and email delivery into one working application."),
    NB(10, "<b>Maintain the project using GitHub</b> - keep source code and documentation in a public repository for accessibility and version control."),
]

# ══════════════ 2. DESIGN APPROACH ══════════════
story += [
    P("2. PORTFOLIO AND DESIGN APPROACH", h1),
    P("The portfolio was designed to be <b>professional, organized, and easy to navigate</b> while "
      "expressing a DevOps engineering identity. The visual concept is a \"living terminal\": a "
      "dark ops-room theme with terminal green and amber accents, monospaced display typography, "
      "terminal-window chrome, and animated command-line sequences."),
    P("2.1 User-Centric Design", h2),
    P("Information is arranged so a visitor understands my profile progressively, in the "
      "following reading order (Figure 1):"),
    Spacer(1, 4),
    flow_snake(["Introduction", "About", "Skills", "Experience",
                "Projects", "Publications", "Education", "Contact"]),
    fig_caption("Figure 1: Portfolio reading order - the visitor's path through the page sections."),
    P("The page opens with a short introduction and moves towards detailed technical and "
      "academic information, ending with clear calls-to-action (resume download and contact form)."),
    P("2.2 Navigation", h2),
    B("A sticky navigation bar with direct links to every section."),
    B("Automatic highlighting of the section currently in view while scrolling."),
    B("A responsive burger menu on mobile screens."),
    B("A resume button always visible in the navigation bar."),
    P("2.3 Visual Design", h2),
    B("Clear section headings with numbered indices and command-style titles (whoami, ls ./skills, git log --projects)."),
    B("Consistent typography: JetBrains Mono for display text, Inter for body text."),
    B("A typed terminal boot sequence, an animated CI/CD pipeline diagram, count-up statistics, an infinite technology marquee, and scroll-reveal animations (anime.js)."),
    B("Project cards with cursor glow, skill chips, timeline draw-on, and a photo scanline effect."),
    B("Accessibility: prefers-reduced-motion disables all animation; semantic landmarks and focus styles are provided."),
    P("2.4 Technical Design", h2),
    P("The website follows a <b>frontend + serverless backend + email delivery</b> architecture:"),
    B("<b>Frontend (static):</b> displays portfolio content, handles navigation, provides the resume download, collects contact information, and sends it to the backend API."),
    B("<b>Backend (Azure Function):</b> receives the contact request, validates submitted data, checks a honeypot anti-spam field, rate-limits by IP, and delivers the message by email."),
    B("<b>Email layer:</b> the primary path sends via SMTP (nodemailer) using credentials stored as encrypted Azure app settings; an automatic fallback delivers through the formsubmit.co service to the same inbox. No database is used - the inbox itself is the record."),
]

# ══════════════ 3. SECTIONS ══════════════
story += [
    PageBreak(),
    P("3. PORTFOLIO SECTIONS AND FUNCTIONALITIES", h1),
    P("3.1 Hero Section", h2),
    P("The homepage opens with an animated terminal that types an SSH session "
      "(ssh devyansh@bengaluru), a JSON profile, and a deploy command. It contains my name, my "
      "professional focus (DevOps and Cloud Engineering), a role statement, a Download Resume "
      "call-to-action, quick facts (location, focus, availability), an animated commit-build-test-deploy "
      "pipeline, and count-up statistics (CGPA, automated tests, publications, projects)."),
    P("3.2 About Section", h2),
    P("A brief description of my academic background (MCA in Storage &amp; Cloud Technology), AWS "
      "Academy Solutions Architect training, hands-on CI/CD exposure, and my Q1-published cloud-security "
      "research. A portrait photo is presented inside a terminal window frame with an animated scanline."),
    P("3.3 Skills Section", h2),
    P("Skills are organized into six cards: cloud &amp; infrastructure, programming &amp; scripting, "
      "containers &amp; CI/CD, DevOps &amp; tooling, networking, and security &amp; testing - each "
      "listing concrete technologies (AWS, Python, SQL, Docker, Jenkins, GitHub Actions, TCP/IP, "
      "penetration testing, and others)."),
    P("3.4 Projects Section", h2),
    B("<b>Abhyas</b> - a study planner and revision platform: pnpm + Turborepo monorepo, ~175 automated tests, CI/CD on GitHub Actions, Supabase PostgreSQL with RLS, offline-first SQLite sync. (Shipped)"),
    B("<b>PolyBot</b> - a low-latency arbitrage trading system: live WebSocket feeds, sub-millisecond detection, deterministic replay backtesting, deployed on Oracle Cloud near the exchange. (Running)"),
    B("<b>MEDBridge</b> - a full-stack team communication app with threads and channels, used as a live college project. (Live)"),
    B("<b>InsightForge</b> - a multimodal AI research assistant processing PDFs, papers, charts, and screenshots with vector databases. (In progress)"),
    P("Each project card shows its technology stack and links to its GitHub repository where available."),
    P("3.5 Experience Section", h2),
    P("A vertical timeline presents: Technical Team Lead (Intern) at Nexathread Pvt Ltd (led a team "
      "of four interns end-to-end), Executive Member of the AWS Club and the IEEE Student Chapter at "
      "Jain University, and freelance cybersecurity &amp; software testing work (penetration testing, "
      "bug-bounty hunting, and QA for a gamified marketplace platform)."),
    P("3.6 Publications Section", h2),
    P("Research work with direct DOI/article links: a Q1 journal article in MethodsX on the forensic "
      "implications of multi-tenancy in cloud computing (AWS-based investigative framework), and a "
      "theoretical article on digital technology use and wellbeing."),
    P("3.7 Education and Certifications Section", h2),
    P("Academic qualifications (MCA - Storage &amp; Cloud Technology, CGPA 8.17/10; BCA) with class "
      "X/XII results, plus certifications with links: AWS Academy Cloud Solutions Architect, LinkedIn "
      "Learning certificates in Generative AI and Network Architecture."),
    P("3.8 Contact Section", h2),
    P("Direct channels (email, phone, LinkedIn, GitHub) alongside a working contact form with name, "
      "email, and message fields, client-side validation, and animated delivery status feedback. The "
      "form is connected to the backend API described in Section 6."),
    P("3.9 Resume Section", h2),
    P("Resume download buttons in the navigation bar, hero, and contact section link directly to the "
      "resume PDF bundled with the website, using the HTML download attribute so the file downloads "
      "with a proper filename in every browser."),
]

# ══════════════ 4. TECHNOLOGIES ══════════════
story += [
    P("4. TECHNOLOGIES USED", h1),
    P("The following technologies and platforms were used to develop and deploy the portfolio."),
    tbl([
        ["Layer", "Technology", "Purpose"],
        ["Frontend", "HTML5, CSS3, JavaScript (ES modules)", "Single-page portfolio, structure, styling, interactivity"],
        ["Animation", "anime.js v4.1.2 (vendored, MIT)", "Entrance choreography, scroll reveals, typing effect, timers"],
        ["Hosting", "Azure Static Web Apps (Free tier)", "Global CDN for static content, managed Functions platform"],
        ["Backend", "Azure Functions v4 (Node 20)", "Serverless contact-form API at /api/contact"],
        ["Email (primary)", "nodemailer over SMTP (Gmail app password)", "Delivers form messages to my personal inbox"],
        ["Email (fallback)", "formsubmit.co AJAX endpoint", "Automatic failover delivery to the same inbox"],
        ["Version control", "Git + GitHub", "Source control, public repository"],
        ["CI/CD", "GitHub Actions", "Automated build and deployment on push to main"],
        ["Verification", "curl, browser developer tools", "Live endpoint, download, and delivery testing"],
    ], widths=[88, 168, 200]),
]

# ══════════════ 5. FRONTEND ══════════════
story += [
    P("5. FRONTEND (PLAIN HTML/CSS/JS + ANIME.JS)", h1),
    P("5.1 No-Framework Frontend", h2),
    P("The frontend is a single semantic HTML page with external CSS and an ES-module JavaScript "
      "file - deliberately no framework and no build step. This keeps the deployment artifact "
      "simple (the repository itself is the build output), removes an entire class of toolchain "
      "maintenance, and keeps the page payload small. The site is divided into clearly identifiable "
      "sections (hero, about, skills, experience, projects, publications, education, contact) so "
      "content is easy to maintain."),
    P("5.2 anime.js v4", h2),
    P("All animation is driven by anime.js v4.1.2, vendored into the repository (vendor/anime.esm.js) "
      "so the site has no CDN dependency and works fully offline. The library provides the typed "
      "terminal boot sequence (createTimer), the hero name reveal (text.split with per-character "
      "gradient repaint), staggered entrance choreography (createTimeline), scroll-triggered section "
      "reveals and timeline draw-on (onScroll), and looping effects (pipeline pulse, marquee, photo "
      "scanline). prefers-reduced-motion is honored throughout: users who request reduced motion get "
      "the full content with animations disabled."),
    P("5.3 Frontend Functionality", h2),
    B("Displaying portfolio content and handling one-page navigation with active-section highlighting."),
    B("Providing project and publication links, and the resume download."),
    B("Validating contact input in the browser before submission."),
    B("Sending contact information to the backend API and displaying animated success/error feedback."),
]

# ══════════════ 6. BACKEND ══════════════
story += [
    P("6. BACKEND AND API (AZURE FUNCTIONS)", h1),
    P("Azure Functions provides the backend of the portfolio using the serverless model: no "
      "continuously running server exists; the function executes only when an HTTP request is "
      "received. The API is implemented with the Azure Functions Node.js v4 programming model "
      "(app.http) and runs on Node 20 as configured in staticwebapp.config.json (apiRuntime)."),
    P("6.1 Contact API", h2),
    P("The contact endpoint processes messages submitted through the portfolio:"),
    tbl([
        ["Endpoint", "Method", "Purpose"],
        ["/api/contact", "POST", "Validate, anti-spam check, rate-limit, and deliver the message by email"],
    ], widths=[110, 70, 276]),
    P("6.2 Backend Processing Steps", h2),
    NB(1, "Parse and validate the JSON body (name, email, message required; field length limits enforced)."),
    NB(2, "Honeypot anti-spam: a hidden \"company\" field invisible to humans; bots that fill it receive a fake success and nothing is sent."),
    NB(3, "Rate limiting: a maximum of 3 submissions per IP address per 10-minute window (in-memory sliding window)."),
    NB(4, "HTML-escape all visitor input before building the email body (injection defence)."),
    NB(5, "Deliver via SMTP using credentials from Azure app settings; the visitor's email is set as the Reply-To address so a reply lands directly in the visitor's inbox."),
    NB(6, "Return a JSON response: 200 on success, 400 invalid input, 429 rate-limited, 502 delivery failure."),
    P("6.3 Backend Processing Flow", h2),
    P("Figure 2 shows the server-side pipeline executed by the Azure Function for every "
      "submission (Figure 3 in Section 7 shows the delivery paths)."),
    Spacer(1, 4),
    flow_v([
        {"t": "Request received", "s": "POST /api/contact (JSON)"},
        {"t": "Parse & validate input"},
        {"t": "Honeypot check", "s": "bots silently dropped"},
        {"t": "Rate limit", "s": "3 per IP / 10 minutes"},
        {"t": "Deliver via SMTP", "s": "Reply-To = visitor"},
        {"t": "JSON response", "s": "200 / 400 / 429 / 502"},
    ]),
    fig_caption("Figure 2: Server-side processing pipeline of the /api/contact Azure Function."),
    Spacer(1, 2),
    P("If the primary SMTP path is unavailable (for example, SMTP credentials are not yet "
      "configured on the deployment), the frontend automatically retries the submission through the "
      "formsubmit.co fallback service, which delivers to the same inbox - so the visitor's message "
      "still arrives (see Section 7)."),
]

# ══════════════ 7. EMAIL DELIVERY ══════════════
story += [
    PageBreak(),
    P("7. EMAIL DELIVERY DESIGN (NO DATABASE)", h1),
    P("A key design decision of this project is that <b>contact messages are delivered directly to "
      "my personal email inbox and are never stored in a database</b>. Submitted information "
      "travels from the browser through the serverless function (or the fallback service) and "
      "terminates in an inbox I already monitor daily."),
    P("7.1 Two Delivery Paths", h2),
    P("Every submission first attempts the primary path; if it fails for any reason, the same "
      "message is automatically retried over the fallback path. Both paths terminate in the same "
      "personal inbox (Figure 3):"),
    B("<b>Primary - SMTP through the Azure Function:</b> the function connects to an SMTP relay using credentials stored as Azure application settings (a Gmail app password) and sends a themed email to the CONTACT_TO inbox with the visitor's address as Reply-To."),
    B("<b>Fallback - formsubmit.co AJAX:</b> if the primary path fails or is not configured, the frontend transparently submits the same message to the formsubmit.co endpoint for the same inbox. This requires no credentials and activated with a single confirmation click sent to the inbox."),
    Spacer(1, 4),
    flow_branch(),
    fig_caption("Figure 3: Two-path email delivery - the primary SMTP route and the automatic "
                "formsubmit.co fallback both terminate in the personal inbox."),
    P("7.2 Why Email-Only", h2),
    NB(1, "<b>Privacy by design:</b> no visitor data is persisted anywhere - there is no database account, no credentials to rotate, and no data-retention surface to secure."),
    NB(2, "<b>Fewer moving parts:</b> the storage account, connection strings, schemas, and data-access code of a database layer are eliminated entirely."),
    NB(3, "<b>Faster to act on:</b> messages arrive where I actually read email, with the sender one click away via Reply-To."),
    NB(4, "<b>Resilience:</b> the automatic fallback guarantees delivery even while the primary SMTP path is being reconfigured."),
    P("7.3 Trade-off", h2),
    P("The inbox itself serves as the archive: submissions are not queryable through an application "
      "API. For a personal portfolio contact form, this is the appropriate trade of queryability "
      "for simplicity and privacy."),
]

# ══════════════ 8. GITHUB & CI/CD ══════════════
story += [
    P("8. GITHUB AND CI/CD ACTIONS", h1),
    P("8.1 GitHub", h2),
    P("GitHub is the central repository for the project, containing the frontend, the Azure "
      "Function source, deployment configuration, and documentation. Git tracks every change to "
      "the project over time, and the repository is publicly accessible for review."),
    P("8.2 GitHub Actions", h2),
    P("GitHub Actions automates the deployment workflow. When changes are pushed to the main "
      "branch, the workflow (azure-static-web-apps-polite-mud-0ba46ac00.yml) performs the "
      "following steps:"),
    NB(1, "Retrieve the latest source code (actions/checkout)."),
    NB(2, "Run the Azure Static Web Apps deploy action with the deployment token stored as a GitHub secret."),
    NB(3, "Publish the static content (app_location: \"/\") and build the managed Functions API (api_location: \"api\")."),
    NB(4, "Update the live site at the public Azure URL (typically within about two minutes)."),
    P("A legacy duplicate workflow file that referenced a misnamed secret was removed during "
      "hardening, leaving a single, working pipeline."),
    P("8.3 CI/CD Pipeline", h2),
    P("The complete development-to-deployment process is automated as shown in Figure 4:"),
    Spacer(1, 4),
    flow_v([
        {"t": "Code change", "s": "local working copy"},
        {"t": "git commit & push", "s": "main branch"},
        {"t": "GitHub Actions workflow", "s": "build & deploy job"},
        {"t": "Azure Static Web Apps", "s": "static content + managed API"},
        {"t": "Live portfolio updated", "s": "public URL, ~2 minutes", "kind": "ok"},
    ]),
    fig_caption("Figure 4: CI/CD pipeline - every push to main is built and deployed to Azure automatically."),
    Spacer(1, 2),
    P("This removes the need to manually upload the website after every change: the repository "
      "is the single source of truth, and the live site always reflects the main branch."),
]

# ══════════════ 9. AZURE ARCHITECTURE ══════════════
story += [
    P("9. AZURE DEPLOYMENT ARCHITECTURE", h1),
    P("The portfolio is deployed on Azure Static Web Apps with a three-layer application architecture:"),
    tbl([
        ["Layer", "Implementation", "Responsibility"],
        ["Frontend layer", "Static content on the SWA global CDN", "Portfolio UI, navigation, resume download, form UI"],
        ["Backend layer", "Managed Azure Functions (Node 20)", "Validation, anti-spam, rate limiting, email dispatch"],
        ["Email layer", "SMTP relay + formsubmit.co fallback", "Final delivery to the personal inbox"],
    ], widths=[95, 165, 196]),
    Spacer(1, 6),
    P("Platform behaviour is controlled by staticwebapp.config.json, which configures: the Node 20 "
      "API runtime; the /api/contact route; a navigation fallback that rewrites unknown paths to "
      "index.html (excluding assets); correct MIME types (webp, json); and global security headers "
      "(X-Content-Type-Options: nosniff, X-Frame-Options: DENY, a strict Referrer-Policy, and a "
      "restrictive Permissions-Policy disabling geolocation, microphone, and camera)."),
    P("9.1 End-to-End Request Flow", h2),
    P("Figure 5 traces a visitor's request across the three layers, from the browser through the "
      "CDN and serverless function to the email layer and personal inbox:"),
    Spacer(1, 4),
    flow_h([
        ("Visitor", "web browser", ""),
        ("Azure SWA", "global CDN", ""),
        ("Function", "/api/contact", ""),
        ("Email layer", "SMTP / fallback", ""),
        ("Inbox", "delivered", "ok"),
    ]),
    fig_caption("Figure 5: End-to-end request flow across the three deployment layers."),
]

# ══════════════ 10. ENV VARS ══════════════
story += [
    P("10. ENVIRONMENT VARIABLE APPROACH", h1),
    P("Environment variables keep sensitive configuration outside the application source code. "
      "The Azure Function reads all credentials from process.env at runtime; the repository "
      "contains only the code that uses the variables, never the credentials themselves."),
    tbl([
        ["Setting", "Purpose"],
        ["SMTP_HOST / SMTP_PORT", "SMTP relay address and port (e.g. smtp.gmail.com:587)"],
        ["SMTP_USER / SMTP_PASS", "SMTP credentials (Gmail app password; never a real account password)"],
        ["CONTACT_TO", "Inbox that receives form messages (my personal email)"],
    ], widths=[170, 286]),
    Spacer(1, 6),
    P("10.1 Local Environment", h2),
    P("During local development, values live in api/local.settings.json, which is excluded from "
      "version control via .gitignore. Local testing can therefore run against a personal SMTP "
      "relay without any secrets entering the repository."),
    P("10.2 Azure Environment (portal configuration)", h2),
    P("On the deployment, the same variables are configured as Azure Static Web Apps application "
      "settings through the Azure portal - no CLI required:"),
    NB(1, "Open the Azure portal (portal.azure.com) and open the Static Web App resource."),
    NB(2, "In the left menu, under Settings, select Environment variables."),
    NB(3, "Select the Production environment."),
    NB(4, "Select + Add, enter the Name and Value pair, and repeat for each setting (SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, SMTP_SECURE, CONTACT_TO)."),
    NB(5, "Select Apply - the settings are encrypted at rest and hot-apply to the managed function."),
    P("The Function reads them through process.env at runtime, so no code change or redeploy "
      "is needed when a secret is set or rotated."),
    P("10.3 Security Considerations", h2),
    B("Credentials are never hard-coded or committed to GitHub."),
    B("The fallback delivery service requires no credentials at all."),
    B("A GitHub repository scan confirms no SMTP credentials or connection strings exist in any tracked file."),
]

# ══════════════ 11. CONTACT FORM ══════════════
story += [
    PageBreak(),
    P("11. CONTACT FORM IMPLEMENTATION", h1),
    P("The Contact Form is the main interactive feature of the portfolio. The form contains three "
      "required fields - name, email, and message - plus a hidden honeypot field. When the user "
      "clicks the submit button, the frontend validates the input and sends the information to "
      "the backend using an HTTP POST request to /api/contact."),
    P("11.1 Contact Form Workflow", h2),
    P("Figure 6 shows the complete user journey from filling in the form to the on-screen "
      "confirmation; the delivery paths behind step 5 are detailed in Figure 3 (Section 7):"),
    Spacer(1, 4),
    flow_v([
        {"t": "Visitor fills the form", "s": "name - email - message"},
        {"t": "Client-side validation", "s": "field highlight + inline error"},
        {"t": "Submit (button locks)", "s": "shows \"transmitting...\""},
        {"t": "POST /api/contact", "s": "server checks (Figure 2)"},
        {"t": "Email delivered", "s": "SMTP or automatic fallback", "kind": "ok"},
        {"t": "Success shown", "s": "message delivered - form resets", "kind": "ok"},
    ]),
    fig_caption("Figure 6: Contact form user journey, from data entry to the delivered confirmation."),
    Spacer(1, 2),
    P("11.2 Validation (Client and Server)", h2),
    B("Client: empty name, invalid email format, or a message shorter than 10 characters highlight the offending field with an inline error."),
    B("Server: 400 for invalid name/email/message lengths; honeypot filled returns a fake success (bots are silently dropped); 429 when an IP exceeds 3 submissions per 10 minutes."),
    P("11.3 User Feedback", h2),
    P("The submit button disables itself and shows \"transmitting...\" while the request is in "
      "flight. On success, the form resets and the status line animates in with a confirmation "
      "message; on failure it shows the error plus my direct email address as a manual fallback. "
      "All feedback respects the reduced-motion accessibility setting."),
]

# ══════════════ 12. TESTING ══════════════
story += [
    P("12. TESTING RESULTS", h1),
    P("Testing was performed on 5 September 2026 against the <b>live deployed application</b> to "
      "verify that the frontend, backend, email delivery, resume download, and CI/CD pipeline were "
      "functioning correctly."),
    P("12.1 Frontend Testing", h2),
    P("The deployed portfolio was opened through the public Azure Static Web Apps URL. The "
      "following were checked: the homepage loads correctly (HTTP 200); navigation works with "
      "active-section highlighting; all portfolio sections render; project and publication links "
      "resolve; the resume buttons are present; and the contact section is accessible with all "
      "form fields. <b>Result: PASS</b>"),
    P("12.2 Resume Download Testing", h2),
    P("The resume link was requested from the live site and returned HTTP 200 with MIME type "
      "application/pdf and a size of 5,993 bytes. The downloaded file was compared byte-for-byte "
      "(cmp) against the repository copy and was identical. The browser download attribute was "
      "confirmed, so the file saves with the correct filename. <b>Result: PASS</b>"),
    P("12.3 Storage-Integration Removal Testing", h2),
    P("The removed Azure Blob Storage endpoint (/api/resume, which previously returned a 503 "
      "configuration error page) now returns HTTP 404, confirming the SAS function and its "
      "dependency (@azure/storage-blob) are fully removed and the direct download is the only "
      "path. <b>Result: PASS</b>"),
    P("12.4 Contact Form End-to-End Testing", h2),
    P("A live submission was made through the deployed portfolio (name: Report Verification). The "
      "browser network log recorded: POST /api/contact returned 502 (the primary SMTP path, whose "
      "app settings are pending configuration), after which the automatic fallback POST to "
      "formsubmit.co returned 200. The website displayed the success message \"message delivered\" "
      "and the message was received in the target inbox. This demonstrates both the end-to-end "
      "delivery and the resilience of the two-path design. <b>Result: PASS</b>"),
    P("12.5 CI/CD Testing", h2),
    P("A push to the main branch triggered GitHub Actions run 33975396152, which built and deployed "
      "the application and completed successfully; the live site reflected the new content "
      "immediately afterwards. <b>Result: PASS</b>"),
    P("12.6 Summary", h2),
    tbl([
        ["Test", "Expected", "Observed", "Result"],
        ["Frontend load & navigation", "Sections render, links work", "All sections and links live (HTTP 200)", "PASS"],
        ["Resume download", "HTTP 200, correct PDF", "200, application/pdf, 5,993 bytes, byte-identical", "PASS"],
        ["Legacy /api/resume removed", "404 (no error page)", "404", "PASS"],
        ["Contact form (primary path)", "Message delivered", "502 - SMTP settings pending", "-"],
        ["Contact form (fallback path)", "Automatic failover delivers", "200 via formsubmit.co; received in inbox", "PASS"],
        ["CI/CD pipeline", "Push deploys automatically", "Run 33975396152 completed successfully", "PASS"],
    ], widths=[118, 118, 160, 42], fs=9),
    Spacer(1, 4),
    P("The complete application flow (Figure 5) was verified end to end: from the browser "
      "through the frontend and the Azure Function (or the fallback service) to the personal "
      "inbox, and back to the browser as a success response."),
]

# ══════════════ 13. SCREENSHOTS ══════════════
story += [
    PageBreak(),
    P("13. PORTFOLIO SCREENSHOTS", h1),
    P("The following screenshots show the deployed portfolio running live on Azure Static Web Apps."),
]
story += img_els([(os.path.join(IMG, "01-hero.png"), 452,
    "Screenshot 1: Deployed homepage (hero) - animated terminal boot sequence, resume "
    "call-to-action, CI/CD pipeline animation, and live statistics."),
])
story += [PageBreak()]
story += img_els([(os.path.join(IMG, "02-contact.png"), 452,
    "Screenshot 2: Contact section - direct channels and the working contact form "
    "(name, email, message) with the resume download button."),
])
story += img_els([(os.path.join(IMG, "03-hero-cta.png"), 452,
    "Screenshot 3: Hero call-to-action area - the Download Resume button linking "
    "directly to the bundled PDF."),
])
story += [PageBreak()]
story += img_els([(os.path.join(IMG, "04-actions-deploy.png"), 452,
    "Screenshot 4: GitHub Actions - the successful build-and-deploy workflow run "
    "(run 33975396152) that published the live site."),
])

# ══════════════ 14. DELIVERY VERIFICATION ══════════════
story += [
    P("14. EMAIL DELIVERY VERIFICATION", h1),
    P("The screenshot below captures the contact form immediately after a real end-to-end "
      "submission on the deployed site. The status line confirms successful delivery. The browser "
      "network log for the same submission recorded the two-path delivery: the primary request to "
      "/api/contact, followed by the automatic fallback to formsubmit.co which completed the "
      "delivery to the personal inbox."),
]
story += img_els([(os.path.join(IMG, "05-form-flow.png"), 452,
    "Screenshot 5: Contact form after live submission - the success message "
    "confirming the message was delivered to the personal inbox."),
])
story += [
    tbl([
        ["Request (browser network log)", "Status"],
        ["POST https://...azurestaticapps.net/api/contact (primary path)", "502 - SMTP app settings pending"],
        ["POST https://formsubmit.co/ajax/... (automatic fallback)", "200 - delivered to inbox"],
    ], widths=[330, 126], fs=9),
    Spacer(1, 4),
    P("This is evidence of the complete delivery flow: Contact Form -&gt; automatic failover "
      "-&gt; email service -&gt; personal inbox. The visitor saw a single, successful "
      "\"message delivered\" confirmation."),
]

# ══════════════ 15/16. LINKS ══════════════
story += [
    PageBreak(),
    P("15. GITHUB AND PORTFOLIO LINKS", h1),
    P("16.1 GitHub Repository", h2),
    P("The complete source code and project files are maintained in the following public GitHub "
      "repository, containing the frontend, the backend/API implementation, deployment "
      "configuration, and project documentation:"),
    P("Devyansh Gupta Portfolio - https://github.com/Devyansh-Gupta/devyansh-gupta-portfolio", flow),
    Spacer(1, 6),
    P("16.2 Live Portfolio", h2),
    P("The deployed portfolio can be accessed using the following public URL:"),
    P("https://polite-mud-0ba46ac00.7.azurestaticapps.net", flow),
    Spacer(1, 6),
    P("The live URL demonstrates that the portfolio has been successfully deployed on Microsoft "
      "Azure and is publicly accessible, with a working serverless contact form delivering "
      "directly to email and a resume downloadable straight from the site."),
]

doc.build(story)
print("BUILT:", OUT, os.path.getsize(OUT), "bytes")

