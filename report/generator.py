from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                 TableStyle, PageBreak)
from reportlab.lib.enums import TA_CENTER, TA_LEFT

def generate_report(visitors, captures):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=20*mm, leftMargin=20*mm,
                            topMargin=20*mm, bottomMargin=20*mm)
    styles = getSampleStyleSheet()
    elements = []

    title_style = ParagraphStyle('CustomTitle', parent=styles['Title'],
                                  fontSize=20, spaceAfter=6, alignment=TA_CENTER,
                                  textColor=colors.HexColor('#0c4a6e'))
    subtitle_style = ParagraphStyle('Subtitle', parent=styles['Normal'],
                                     fontSize=11, alignment=TA_CENTER,
                                     textColor=colors.HexColor('#4b5563'),
                                     spaceAfter=20)
    h2 = ParagraphStyle('H2', parent=styles['Heading2'],
                         fontSize=14, textColor=colors.HexColor('#0c4a6e'),
                         spaceAfter=10, spaceBefore=20)
    normal = styles['Normal']
    small = ParagraphStyle('Small', parent=normal, fontSize=8, leading=12)

    elements.append(Paragraph("LAPORAN DEMO PHISHKIT", title_style))
    elements.append(Paragraph("Cybersecurity Seminar — Simulasi Phishing", subtitle_style))
    tgl = datetime.now().strftime('%d %B %Y, %H:%M')
    elements.append(Paragraph(f"<b>Tanggal:</b> {tgl}", normal))
    elements.append(Paragraph(f"<b>Total Pengunjung:</b> {len(visitors)}", normal))
    elements.append(Paragraph(f"<b>Total Credential Tertangkap:</b> {len(captures)}", normal))
    elements.append(Spacer(1, 15))

    if captures:
        elements.append(Paragraph("DATA CREDENTIAL YANG TERTANGKAP", h2))
        data = [['#', 'Template', 'Username / Email', 'Password', 'Waktu']]
        for i, c in enumerate(captures[:30], 1):
            data.append([
                str(i),
                c.get('template', '-'),
                c.get('username', '-'),
                c.get('password', '-'),
                c.get('timestamp', '-')[:19]
            ])
        col_w = [20, 70, 140, 140, 100]
        t = Table(data, colWidths=[w*mm for w in [8, 25, 50, 50, 35]])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0c4a6e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f1f5f9')]),
        ]))
        elements.append(t)
        elements.append(Spacer(1, 10))

    if visitors:
        elements.append(Paragraph("RIWAYAT PENGUNJUNG", h2))
        vdata = [['#', 'Template', 'Browser', 'Waktu']]
        for i, v in enumerate(visitors[:30], 1):
            ua = v.get('user_agent', '')
            browser = 'Chrome'
            if 'Edg' in ua: browser = 'Edge'
            elif 'Firefox' in ua: browser = 'Firefox'
            elif 'Safari' in ua: browser = 'Safari'
            vdata.append([str(i), v.get('template', '-'), browser, v.get('timestamp', '-')[:19]])
        vt = Table(vdata, colWidths=[8*mm, 30*mm, 50*mm, 35*mm])
        vt.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0c4a6e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f1f5f9')]),
        ]))
        elements.append(vt)

    elements.append(PageBreak())
    elements.append(Paragraph("EDUKASI ANTI-PHISHING", h2))
    tips = [
        "1. <b>Periksa URL</b> — Pastikan domain sesuai. Phishing sering gunakan domain mirip (typosquatting).",
        "2. <b>Jangan klik link mencurigakan</b> — Arahkan kursor untuk lihat URL sebenarnya sebelum klik.",
        "3. <b>Perhatikan tanda bahaya</b> — Email mendesak, ancaman, atau tawaran terlalu bagus bisa jadi phishing.",
        "4. <b>Aktifkan 2FA</b> — Autentikasi dua faktor melindungi meskipun password bocor.",
        "5. <b>Gunakan Password Manager</b> — Tidak akan auto-fill di situs phishing karena domain berbeda.",
        "6. <b>Laporkan</b> — Jika menerima email phishing, laporkan ke tim IT/keamanan.",
    ]
    for tip in tips:
        elements.append(Paragraph(tip, normal))
        elements.append(Spacer(1, 6))

    elements.append(Spacer(1, 20))
    note_style = ParagraphStyle('Note', parent=normal,
                                 fontSize=8, textColor=colors.grey,
                                 alignment=TA_CENTER)
    elements.append(Paragraph(
        "<i>Laporan ini digenerate otomatis oleh PhishKit — Tool Edukasi Cybersecurity.</i>",
        note_style))

    doc.build(elements)
    buffer.seek(0)
    return buffer