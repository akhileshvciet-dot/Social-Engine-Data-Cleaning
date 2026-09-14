import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import re
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib import colors
from reportlab.platypus import PageBreak, Paragraph, Spacer, Image, Table, TableStyle, BaseDocTemplate
from reportlab.platypus import PageTemplate, Frame
from reportlab.pdfgen import canvas

BASE = r'C:\Users\Admin\Desktop\DataVortex'
CHART_DIR = BASE + r'\eda_charts'
REPORT_PATH = BASE + r'\EDA_Report.pdf'

import os
os.makedirs(CHART_DIR, exist_ok=True)

sns.set_theme(style='whitegrid')
plt.rcParams['font.size'] = 9
plt.rcParams['figure.dpi'] = 100

posts = pd.read_csv(BASE + r'\Social_Engine_Posts_Cleaned.csv')
users = pd.read_csv(BASE + r'\Social_Engine_Users_Cleaned.csv')

posts['timestamp'] = pd.to_datetime(posts['timestamp'], format='%Y-%m-%dT%H:%M:%S', errors='coerce')
posts['likes'] = pd.to_numeric(posts['likes'], errors='coerce')
posts['shares'] = pd.to_numeric(posts['shares'], errors='coerce')
posts['comments'] = pd.to_numeric(posts['comments'], errors='coerce')
posts['text_len'] = posts['text_content'].fillna('').str.len()

# ---- 1. Posts by platform
plt.figure(figsize=(6, 3.6))
order = posts['platform'].value_counts().index
sns.countplot(data=posts, y='platform', order=order)
plt.title('Number of Posts by Platform')
plt.xlabel('Count')
plt.ylabel('Platform')
plt.tight_layout()
plt.savefig(CHART_DIR + r'\platform.png')
plt.close()

# ---- 2. Likes distribution
plt.figure(figsize=(6, 3.6))
sns.histplot(posts['likes'], bins=30, kde=True)
plt.title('Distribution of Likes')
plt.xlabel('Likes')
plt.ylabel('Frequency')
plt.tight_layout()
plt.savefig(CHART_DIR + r'\likes.png')
plt.close()

# ---- 3. Posts over time
plt.figure(figsize=(6, 3.6))
posts['year_month'] = posts['timestamp'].dt.to_period('M')
ts = posts.groupby('year_month').size()
ts.plot(marker='o', markersize=3)
plt.title('Posts per Month')
plt.xlabel('Month')
plt.ylabel('Number of Posts')
plt.tight_layout()
plt.savefig(CHART_DIR + r'\timeline.png')
plt.close()

# ---- 4. Top hashtags
def extract_hashtags(text):
    return re.findall(r'#(\w+)', str(text))
tags = Counter()
for t in posts['text_content'].dropna():
    tags.update(extract_hashtags(t))
top_tags = tags.most_common(15)
plt.figure(figsize=(6, 3.6))
plt.barh([t for t, _ in reversed(top_tags)], [c for _, c in reversed(top_tags)], color='steelblue')
plt.title('Top 15 Hashtags')
plt.xlabel('Occurrences')
plt.tight_layout()
plt.savefig(CHART_DIR + r'\hashtags.png')
plt.close()

# ---- 5. Correlation heatmap
plt.figure(figsize=(4.5, 3.6))
corr = posts[['likes', 'shares', 'comments']].corr()
sns.heatmap(corr, annot=True, cmap='coolwarm', vmin=-1, vmax=1, cbar=False)
plt.title('Correlation: Likes / Shares / Comments')
plt.tight_layout()
plt.savefig(CHART_DIR + r'\corr.png')
plt.close()

# ---- 6. Text length distribution
plt.figure(figsize=(6, 3.6))
sns.histplot(posts['text_len'], bins=30, kde=True)
plt.title('Distribution of Text Length')
plt.xlabel('Characters')
plt.ylabel('Frequency')
plt.tight_layout()
plt.savefig(CHART_DIR + r'\textlen.png')
plt.close()

# ---- 7. User language
plt.figure(figsize=(6, 3.6))
lang_order = users['language'].value_counts().index[:10]
sns.countplot(data=users, y='language', order=lang_order)
plt.title('Top 10 User Languages')
plt.xlabel('Count')
plt.ylabel('Language')
plt.tight_layout()
plt.savefig(CHART_DIR + r'\lang.png')
plt.close()

# ---- 8. Follower count distribution
plt.figure(figsize=(6, 3.6))
sns.histplot(users['follower_count'], bins=30, kde=True)
plt.title('Distribution of Follower Counts')
plt.xlabel('Followers')
plt.ylabel('Frequency')
plt.tight_layout()
plt.savefig(CHART_DIR + r'\followers.png')
plt.close()

print('Charts generated.')

# ==================== PDF REPORT (professional layout) ====================

# ---- Team / report metadata ----
TEAM_NAME = 'TEAM NEXUS'
TEAM_ID = '10698'

# ---- Color palette (Spiced Orange theme) ----
NAVY = colors.HexColor('#9A3412')     # deep burnt-orange header
BLUE = colors.HexColor('#EA580C')     # vivid orange accent
LIGHT_BLUE = colors.HexColor('#FDEDE3')  # soft peach background
GOLD = colors.HexColor('#F59E0B')     # amber highlight
DARK_TEXT = colors.HexColor('#431407')  # near-black warm brown
GREY = colors.HexColor('#808080')
LIGHT_GREY = colors.HexColor('#F7F1EC')


def add_header_footer(canv, doc):
    """Blue band header on each page + footer with page number."""
    width, height = A4
    # Header bar
    canv.saveState()
    canv.setFillColor(NAVY)
    canv.rect(0, height - 38, width, 38, stroke=0, fill=1)
    canv.setFillColor(GOLD)
    canv.rect(0, height - 40, width, 2, stroke=0, fill=1)
    # Header text
    canv.setFillColor(colors.white)
    canv.setFont('Times-Bold', 8)
    canv.drawString(36, height - 26, f'{TEAM_NAME}  |  Team ID: {TEAM_ID}')
    canv.setFont('Times-Roman', 8)
    canv.drawRightString(width - 36, height - 26, 'DataVortex - Social Engine EDA Report')
    # Footer line + page number
    canv.setStrokeColor(LIGHT_GREY)
    canv.setLineWidth(0.75)
    canv.line(36, 34, width - 36, 34)
    canv.setFillColor(GREY)
    canv.setFont('Times-Roman', 8)
    canv.drawCentredString(width / 2, 22, f'Page {canv.getPageNumber()}')
    canv.drawString(36, 22, 'Confidential - For hackathon evaluation')
    canv.restoreState()


doc = BaseDocTemplate(REPORT_PATH, pagesize=A4,
                      leftMargin=36, rightMargin=36, topMargin=70, bottomMargin=52)
frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id='main')
doc.addPageTemplates([PageTemplate(id='all', frames=[frame], onPage=add_header_footer)])

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='CenterTitle', parent=styles['Title'], alignment=TA_CENTER,
                          textColor=DARK_TEXT, fontSize=22, spaceAfter=6, fontName='Times-Bold'))
styles.add(ParagraphStyle(name='SubTitle', parent=styles['Normal'], alignment=TA_CENTER,
                          fontSize=12, textColor=BLUE, spaceAfter=2))
styles.add(ParagraphStyle(name='TeamLine', parent=styles['Normal'], alignment=TA_CENTER,
                          fontSize=11, textColor=GOLD, fontName='Times-Bold', spaceAfter=2))
styles.add(ParagraphStyle(name='H2', parent=styles['Heading2'], fontSize=13,
                          textColor=DARK_TEXT, spaceBefore=12, spaceAfter=6, fontName='Times-Bold'))
styles.add(ParagraphStyle(name='Body', parent=styles['Normal'], fontSize=10, leading=14))

story = []

# ---- Title block (with border frame) ----
title_tbl = Table([
    [Paragraph('EXPLORATORY DATA ANALYSIS REPORT', styles['CenterTitle'])],
    [Paragraph('Social Engine - Posts & Users Dataset', styles['SubTitle'])],
    [Paragraph(f'{TEAM_NAME}  -  Team ID: {TEAM_ID}', styles['TeamLine'])],
    [Paragraph('DataVortex Hackathon  |  Round 1', styles['SubTitle'])],
], colWidths=[doc.width])
title_tbl.setStyle(TableStyle([
    ('BOX', (0, 0), (-1, -1), 1.2, NAVY),
    ('LINEBEFORE', (0, 0), (0, -1), 6, GOLD),
    ('BACKGROUND', (0, 0), (-1, -1), LIGHT_BLUE),
    ('TOPPADDING', (0, 0), (-1, 0), 16),
    ('BOTTOMPADDING', (0, -1), (-1, -1), 16),
    ('TOPPADDING', (0, 1), (-1, -2), 4),
    ('BOTTOMPADDING', (0, 1), (-1, -2), 4),
]))
story.append(title_tbl)
story.append(Spacer(1, 14))


def border_style(tbl, n_rows, header_rows=1):
    """Consistent professional borders: navy box, gold top rule, zebra rows."""
    s = [
        ('BOX', (0, 0), (-1, -1), 1, BLUE),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#F1C7A8')),
        ('LINEABOVE', (0, 0), (-1, 0), 1.2, GOLD),
        ('BACKGROUND', (0, 0), (-1, 0), NAVY),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]
    # Zebra striping
    for r in range(1, n_rows):
        if r % 2 == 1:
            s.append(('BACKGROUND', (0, r), (-1, r), LIGHT_GREY))
    return s


def figure_block(img_path, caption):
    """Image with a surrounding box + caption bar underneath."""
    img_tbl = Table([[Image(img_path, width=5.4 * inch, height=3.4 * inch, hAlign='CENTER')]],
                    colWidths=[6.0 * inch])
    img_tbl.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 1, BLUE),
        ('BACKGROUND', (0, 0), (-1, -1), colors.white),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    cap = Table([[Paragraph(caption, ParagraphStyle(
        'FigureCap', parent=styles['Body'], alignment=TA_CENTER,
        textColor=colors.white, fontSize=9, fontName='Helvetica-Bold'))]],
        colWidths=[6.0 * inch])
    cap.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), NAVY),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    return Table([[img_tbl], [cap]], colWidths=[6.0 * inch])


def section_banner(text):
    """Gold-accented section heading."""
    tbl = Table([[Paragraph(text, ParagraphStyle(
        'SecHead', parent=styles['H2'], textColor=colors.white,
        fontSize=12, fontName='Helvetica-Bold'))]],
        colWidths=[doc.width])
    tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), BLUE),
        ('LINEBELOW', (0, 0), (-1, -1), 2, GOLD),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    return tbl


# ---- Section 1 ----
story.append(section_banner('1. Dataset Overview'))
story.append(Spacer(1, 6))
overview = Table([
    ['', 'Posts', 'Users'],
    ['Rows', f"{len(posts):,}", f"{len(users):,}"],
    ['Columns', len(posts.columns), len(users.columns)],
    ['Missing values', int(posts.isna().sum().sum()), int(users.isna().sum().sum())],
], colWidths=[2.2 * inch, 2.2 * inch, 2.2 * inch])
overview.setStyle(border_style(overview, len(overview._cellvalues)))
story.append(overview)
story.append(Spacer(1, 10))

# ---- Section 2 ----
story.append(section_banner('2. Descriptive Statistics - Engagement Metrics'))
story.append(Spacer(1, 6))
stats = ['likes', 'shares', 'comments']
stats_table_data = [['Statistic'] + [c.capitalize() for c in stats]]
for stat in ['count', 'mean', 'median', 'min', 'max', 'std']:
    if stat == 'count':
        vals = [f"{posts[c].count():,.0f}" for c in stats]
    elif stat == 'mean':
        vals = [f"{posts[c].mean():,.1f}" for c in stats]
    elif stat == 'median':
        vals = [f"{posts[c].median():,.0f}" for c in stats]
    elif stat == 'min':
        vals = [f"{posts[c].min():,.0f}" for c in stats]
    elif stat == 'max':
        vals = [f"{posts[c].max():,.0f}" for c in stats]
    else:
        vals = [f"{posts[c].std():,.1f}" for c in stats]
    stats_table_data.append([stat.title()] + vals)
st_tbl = Table(stats_table_data, colWidths=[1.6 * inch] + [1.4 * inch] * 3)
st_tbl.setStyle(border_style(st_tbl, len(st_tbl._cellvalues)))
story.append(st_tbl)
story.append(Spacer(1, 6))

# Users stats mini-table
usr_tbl_data = [['Followers - Count', 'Mean', 'Median', 'Max']]
uc = users['follower_count'].dropna()
usr_tbl_data.append([f'{int(uc.count()):,}', f'{uc.mean():,.0f}',
                     f'{uc.median():,.0f}', f'{uc.max():,.0f}'])
usr_tbl = Table(usr_tbl_data, colWidths=[1.8 * inch] + [1.4 * inch] * 3)
usr_tbl.setStyle(border_style(usr_tbl, len(usr_tbl._cellvalues)))
story.append(usr_tbl)
story.append(Spacer(1, 12))

# ---- Section 3 ----
story.append(PageBreak())
story.append(section_banner('3. Visualizations'))
story.append(Spacer(1, 8))
chart_info = [
    (r'\platform.png', 'Figure 1: Number of posts published per platform.'),
    (r'\likes.png', 'Figure 2: Distribution of likes across posts.'),
    (r'\timeline.png', 'Figure 3: Volume of posts published per month.'),
    (r'\hashtags.png', 'Figure 4: Top 15 hashtags used in post content.'),
    (r'\corr.png', 'Figure 5: Correlation between engagement metrics.'),
    (r'\textlen.png', 'Figure 6: Distribution of post text length.'),
    (r'\lang.png', 'Figure 7: Top 10 languages among dataset users.'),
    (r'\followers.png', 'Figure 8: Distribution of user follower counts.'),
]
for i, (fname, caption) in enumerate(chart_info):
    story.append(figure_block(CHART_DIR + fname, caption))
    if i % 2 == 1:
        story.append(Spacer(1, 8))
        story.append(PageBreak())
    else:
        story.append(Spacer(1, 8))

# ---- Section 4 ----
story.append(section_banner('4. Key Insights'))
story.append(Spacer(1, 6))
platform_top = posts['platform'].value_counts().idxmax()
avg_likes = posts['likes'].mean()
avg_shares = posts['shares'].mean()
avg_comments = posts['comments'].mean()
top_tag = top_tags[0]
insight_items = [
    f"<b>Platforms:</b> {len(posts['platform'].unique())} platforms are represented; the most active "
    f"community is <b>{platform_top}</b> with the highest post volume.",
    f"<b>Engagement:</b> On average each post receives {avg_likes:,.1f} likes, "
    f"{avg_shares:,.1f} shares and {avg_comments:,.1f} comments. Likes and comments are strongly "
    f"correlated, suggesting engaged audiences drive both signals together.",
    f"<b>Activity over time:</b> Posting volume fluctuates by month and mirrors campaign "
    f"seasons (BlackFriday, BackToSchool, CyberMonday, etc.).",
    f"<b>Hashtags:</b> The most frequent hashtag is <b>#{top_tag[0]}</b> ({top_tag[1]} uses), "
    f"followed by promotion and product-launch themed tags.",
    f"<b>Users:</b> {len(users):,} unique users are included; follower counts are right-skewed, "
    f"with a small number of high-influence accounts and a long tail of smaller creators.",
    f"<b>Data quality:</b> After cleaning there are no missing values. Missing platforms were "
    f"labelled 'Unknown', missing text replaced with '[No text]', and missing likes imputed "
    f"with the dataset median (robust to outliers).",
]
ins_rows = [[Paragraph(f'<b>{i}.</b>', styles['Body']),
             Paragraph(ins, styles['Body'])] for i, ins in enumerate(insight_items, 1)]
ins_tbl = Table(ins_rows, colWidths=[0.35 * inch, 6.6 * inch])
ins_tbl.setStyle(TableStyle([
    ('BOX', (0, 0), (-1, -1), 1, BLUE),
    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ('TOPPADDING', (0, 0), (-1, -1), 6),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ('LINEBELOW', (0, 0), (-1, -2), 0.5, colors.HexColor('#EDC1A0')),
]))
story.append(ins_tbl)

# ---- Appendix: cleaning summary ----
story.append(Spacer(1, 12))
story.append(section_banner('5. Data Cleaning Summary'))
story.append(Spacer(1, 6))
clean_rows = [
    ['Issue', 'Treatment'],
    ['NULL / empty platform', 'Replaced with "Unknown"'],
    ['NULL / empty text_content', 'Replaced with "[No text]" placeholder'],
    ['Missing likes', 'Imputed with median (2500)'],
    ['Negative like counts', 'Converted to absolute value'],
    ['Mixed timestamp formats', 'Normalized to ISO 8601 (YYYY-MM-DDTHH:MM:SS)'],
    ['HTML entities / tags (&amp;, <div>, <br>)', 'Decoded / stripped'],
    ['Encoding artifacts (Ã©)', 'Corrected to unicode (é)'],
    ['Multi-line quoted records', 'Merged into single logical rows'],
]
clean_tbl = Table(clean_rows, colWidths=[3.2 * inch, 3.8 * inch])
clean_tbl.setStyle(border_style(clean_tbl, len(clean_tbl._cellvalues)))
story.append(clean_tbl)

doc.build(story)
print('PDF report generated:', REPORT_PATH)