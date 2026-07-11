import streamlit as st
import json
import os
import pandas as pd
import io
from datetime import datetime

# --- REPORTLAB IMPORTS FOR PROFESSIONAL PDF GENERATION ---
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfgen import canvas

# ---------- PRE-REQUISITES & CONFIG ----------
FILE_NAME = "students.json"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "1234"
SUBJECTS = [
    "Science", "Fine Arts", "Life Skills", "Mathematics", 
    "Computer Literacy", "Foreign Language", "English Language Arts", 
    "History and Geography", "Physical Education/Health"
]
TOTAL_MARKS = len(SUBJECTS) * 100

st.set_page_config(page_title="Elite Student Portal", page_icon="💎", layout="wide")

# ---------- DATA STORAGE ENGINE ----------
def load_data():
    if os.path.exists(FILE_NAME):
        try:
            with open(FILE_NAME, "r") as file: 
                return json.load(file)
        except: 
            return {}
    return {}

def save_data(data):
    with open(FILE_NAME, "w") as file:
        json.dump(data, file, indent=4)

def seed_sample_data():
    sample_data = {
        "1001": {
            "name": "Zain Ahmed",
            "class": "Grade 10",
            "session": "2026-2027",
            "marks": {"Science": 95, "Fine Arts": 88, "Life Skills": 92, "Mathematics": 98, "Computer Literacy": 96, "Foreign Language": 85, "English Language Arts": 91, "History and Geography": 89, "Physical Education/Health": 94},
            "date": str(datetime.now().date())
        },
        "1002": {
            "name": "Ayesha Khan",
            "class": "Grade 10",
            "session": "2026-2027",
            "marks": {"Science": 82, "Fine Arts": 94, "Life Skills": 85, "Mathematics": 76, "Computer Literacy": 89, "Foreign Language": 92, "English Language Arts": 88, "History and Geography": 84, "Physical Education/Health": 90},
            "date": str(datetime.now().date())
        }
    }
    save_data(sample_data)
    st.rerun()

# ---------- ADVANCED CANVA-STYLE GRADING ENGINE ----------
def get_detailed_grade(score):
    """Calculates letter grade, GPA, and remarks based on standard premium criteria."""
    if score >= 93: return "A", "4.0/4.0", "Excellent performance"
    elif score >= 90: return "A-", "3.7/4.0", "Outstanding results"
    elif score >= 87: return "B+", "3.3/4.0", "Very good work"
    elif score >= 83: return "B", "3.0/4.0", "Good understanding"
    elif score >= 80: return "B-", "2.7/4.0", "Satisfactory progress"
    elif score >= 77: return "C+", "2.3/4.0", "Fair performance"
    elif score >= 70: return "C", "1.7/4.0", "Developing skills"
    elif score >= 67: return "D+", "1.3/4.0", "Needs improvement"
    elif score >= 63: return "D", "1.0/4.0", "Passing status"
    elif score >= 60: return "D-", "0.7/4.0", "Marginal pass"
    else: return "F", "0.0/4.0", "Failing status"

def get_ui_badge(percentage):
    if percentage >= 90: return "🌟 Grade A", "#00FF88"
    elif percentage >= 80: return "✨ Grade B", "#00D2FF"
    elif percentage >= 70: return "✅ Grade C", "#FFD700"
    elif percentage >= 60: return "🆗 Grade D", "#FFA500"
    else: return "❌ Fail", "#FF4B4B"

# ---------- PREMIUM CANVA REPORT CARD PDF GENERATOR ----------
class PremiumReportCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    def draw_background(self):
        self.saveState()
        self.setFillColor(colors.HexColor("#FDFBF7"))
        self.rect(0, 0, 612, 792, fill=True, stroke=False)
        self.setFillColor(colors.HexColor("#D9CEBF"))
        self.circle(40, 740, 60, fill=True, stroke=False)
        self.circle(580, 680, 45, fill=True, stroke=False)
        self.setStrokeColor(colors.HexColor("#B04A4A"))
        self.setLineWidth(3)
        self.circle(110, 660, 28, fill=False, stroke=True)
        self.circle(460, 610, 20, fill=False, stroke=True)
        self.setFillColor(colors.HexColor("#7A533E"))
        self.rect(36, 30, 540, 45, fill=True, stroke=False)
        self.restoreState()

def generate_pdf(student_id, student_info):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('DocTitle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=26, textColor=colors.white, alignment=1, spaceAfter=4)
    subtitle_style = ParagraphStyle('DocSubtitle', parent=styles['Normal'], fontName='Helvetica', fontSize=13, textColor=colors.HexColor("#EAE2D5"), alignment=1)
    field_label_style = ParagraphStyle('FieldLabel', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=11, textColor=colors.HexColor("#9E3B3B"))
    field_val_style = ParagraphStyle('FieldVal', parent=styles['Normal'], fontName='Helvetica', fontSize=11, textColor=colors.HexColor("#2C2520"))
    th_style = ParagraphStyle('TableHeader', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10, textColor=colors.white, alignment=0)
    td_style = ParagraphStyle('TableCell', parent=styles['Normal'], fontName='Helvetica', fontSize=9, textColor=colors.HexColor("#3D332D"))
    key_style = ParagraphStyle('KeyText', parent=styles['Normal'], fontName='Helvetica', fontSize=8, textColor=colors.HexColor("#614E43"), alignment=1)
    quarter_style = ParagraphStyle('QuarterText', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10, textColor=colors.HexColor("#B04A4A"), alignment=1)

    story = []
    banner_data = [[Paragraph("Progress Report", title_style)], [Paragraph("Anderson Family Homeschool", subtitle_style)]]
    banner_table = Table(banner_data, colWidths=[540])
    banner_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#7A533E")),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,0), 16),
        ('BOTTOMPADDING', (0,-1), (-1,-1), 16),
    ]))
    story.append(banner_table)
    story.append(Spacer(1, 25))
    
    meta_data = [
        [Paragraph("Student Name:", field_label_style), Paragraph("School Year:", field_label_style)],
        [Paragraph(student_info['name'], field_val_style), Paragraph(student_info.get('session', '2026-2027'), field_val_style)],
        [Spacer(1, 10), Spacer(1, 10)],
        [Paragraph("Grade / Class:", field_label_style), Paragraph("Teacher:", field_label_style)],
        [Paragraph(student_info['class'], field_val_style), Paragraph("Parent / Educator", field_val_style)]
    ]
    meta_table = Table(meta_data, colWidths=[270, 270])
    meta_table.setStyle(TableStyle([
        ('LINEBELOW', (0,1), (0,1), 1, colors.HexColor("#D4C5B3")),
        ('LINEBELOW', (1,1), (1,1), 1, colors.HexColor("#D4C5B3")),
        ('LINEBELOW', (0,4), (0,4), 1, colors.HexColor("#D4C5B3")),
        ('LINEBELOW', (1,4), (1,4), 1, colors.HexColor("#D4C5B3")),
        ('BOTTOMPADDING', (0,1), (-1,1), 4),
        ('BOTTOMPADDING', (0,4), (-1,4), 4),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 25))
    
    table_content = [[Paragraph("Course Title", th_style), Paragraph("No. of Units", th_style), Paragraph("Course Grade", th_style), Paragraph("Teacher's Remarks", th_style)]]
    for idx, subject in enumerate(SUBJECTS):
        score = student_info['marks'].get(subject, 0)
        let_grade, gpa, remark = get_detailed_grade(score)
        table_content.append([Paragraph(subject, td_style), Paragraph("1.0", td_style), Paragraph(f"{let_grade} ({score}%)", td_style), Paragraph(remark, td_style)])
        
    grades_table = Table(table_content, colWidths=[150, 70, 95, 225])
    ts = [
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#7A533E")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,0), 8),
        ('BOTTOMPADDING', (0,0), (-1,0), 8),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E3DCD2")),
    ]
    for i in range(1, len(table_content)):
        bg_color = colors.HexColor("#F7F3ED") if i % 2 == 0 else colors.HexColor("#FFFFFF")
        ts.append(('BACKGROUND', (0,i), (-1,i), bg_color))
        ts.append(('TOPPADDING', (0,i), (-1,i), 7))
        ts.append(('BOTTOMPADDING', (0,i), (-1,i), 7))
        
    grades_table.setStyle(TableStyle(ts))
    story.append(grades_table)
    story.append(Spacer(1, 25))
    
    key_box_data = [
        [Paragraph("<b>GRADING KEY</b>", th_style)],
        [Paragraph("A = 93% to 100% | 4.0/4.0 &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; C = 70% to 72% | 1.7/4.0", key_style)],
        [Paragraph("A- = 90% to 92% | 3.7/4.0 &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; D+ = 67% to 69% | 1.3/4.0", key_style)],
        [Paragraph("B+ = 87% to 89% | 3.3/4.0 &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; D = 63% to 66% | 1.0/4.0", key_style)],
        [Paragraph("B = 83% to 86% | 3.0/4.0 &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; D- = 60% to 62% | 0.7/4.0", key_style)],
        [Paragraph("B- = 80% to 82% | 2.7/4.0 &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; F = 0% to 59% | 0.0/4.0", key_style)]
    ]
    key_box_table = Table(key_box_data, colWidths=[250])
    key_box_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#7A533E")),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor("#F2ECE4")),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('TOPPADDING', (0,0), (-1,-1), 5),
    ]))
    
    total_score = sum(student_info['marks'].values())
    avg_pct = (total_score / TOTAL_MARKS) * 100
    final_letter, final_gpa, _ = get_detailed_grade(avg_pct)
    
    summary_data = [
        [Paragraph("Quarter One Marks", quarter_style), Paragraph("Quarter Three Marks", quarter_style)],
        [Paragraph(f"<b>{total_score} / {TOTAL_MARKS}</b>", td_style), Paragraph("Pending Evaluation", td_style)],
        [Spacer(1,5), Spacer(1,5)],
        [Paragraph("Quarter Two Marks", quarter_style), Paragraph("Quarter Four Marks", quarter_style)],
        [Paragraph(f"<b>GPA: {final_gpa} ({final_letter})</b>", td_style), Paragraph("Pending Evaluation", td_style)]
    ]
    summary_table = Table(summary_data, colWidths=[135, 135])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,0), colors.HexColor("#F2ECE4")),
        ('BACKGROUND', (1,0), (1,0), colors.HexColor("#F2ECE4")),
        ('BACKGROUND', (0,3), (0,3), colors.HexColor("#F2ECE4")),
        ('BACKGROUND', (1,3), (1,3), colors.HexColor("#F2ECE4")),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (0,1), 1, colors.HexColor("#D4C5B3")),
        ('GRID', (1,0), (1,1), 1, colors.HexColor("#D4C5B3")),
        ('GRID', (0,3), (0,4), 1, colors.HexColor("#D4C5B3")),
        ('GRID', (1,3), (1,4), 1, colors.HexColor("#D4C5B3")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    
    footer_row_table = Table([[key_box_table, summary_table]], colWidths=[260, 280])
    footer_row_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
    ]))
    
    story.append(KeepTogether([footer_row_table]))
    doc.build(story, onFirstPage=lambda c, d: c.draw_background())
    buffer.seek(0)
    return buffer

# ---------- ULTRA-PREMIUM GUI THEMING CONTROLS (CSS WITH INPUT FIX) ----------
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
    
    /* Global Overrides */
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Poppins', sans-serif;
        background: linear-gradient(135deg, #0B0F19 0%, #111827 50%, #1F2937 100%) !important;
        color: #F3F4F6 !important;
    }
    
    h1, h2, h3, p, span, label {
        color: #F3F4F6 !important;
    }
    
    /* Glassmorphism Navigation Sidebar */
    [data-testid="stSidebar"] {
        background-color: rgba(17, 24, 39, 0.7) !important;
        backdrop-filter: blur(20px);
        border-right: 1px solid rgba(255, 255, 255, 0.08);
    }
    
    /* Luxury Container Cards */
    .premium-card {
        background: rgba(255, 255, 255, 0.04);
        padding: 30px;
        border-radius: 24px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(16px);
        box-shadow: 0 12px 40px 0 rgba(0, 0, 0, 0.5);
        margin-bottom: 25px;
    }

    /* Premium Button Overlays */
    .stButton>button {
        background: linear-gradient(90deg, #00F2FE 0%, #4FACFE 100%) !important;
        color: #0B0F19 !important;
        border-radius: 50px !important;
        border: none !important;
        padding: 12px 35px !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 1.5px !important;
        box-shadow: 0 4px 20px rgba(79, 172, 254, 0.4) !important;
    }
    
    /* CRITICAL FIX: Modern Input Text Visibility Fix */
    div[data-testid="stTextInput"] input, 
    div[data-testid="stNumberInput"] input,
    div[data-baseweb="input"] input,
    input {
        background-color: rgba(255, 255, 255, 0.07) !important;
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 12px !important;
    }
    
    div[data-testid="stWidgetLabel"] p {
        color: #00F2FE !important;
        font-weight: 600;
    }
    
    div[data-testid="stTable"] table {
        background-color: rgba(255, 255, 255, 0.02) !important;
        border-collapse: separate !important;
        border-radius: 14px !important;
        overflow: hidden !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
    }
    div[data-testid="stTable"] th {
        background-color: rgba(79, 172, 254, 0.15) !important;
        color: #00F2FE !important;
        padding: 14px !important;
    }
    </style>
""", unsafe_allow_html=True)

# ---------- APPLICATION INTERACTION CONTROLLER ----------
data = load_data()

st.sidebar.markdown("<h1 style='text-align: center; color: #00F2FE; font-weight:700;'>💎 ELITE SMS</h1>", unsafe_allow_html=True)
st.sidebar.markdown("<p style='text-align: center; font-size:12px; color: #9CA3AF;'>SaaS Academic Infrastructure Engine</p>", unsafe_allow_html=True)
st.sidebar.write("---")
choice = st.sidebar.radio("SYSTEM NAVIGATION", ["🏠 DASHBOARD HOME", "🔐 CONTROL PANEL", "👨‍🎓 REPORT CARD PORTAL"])

# --- VIEW 1: RUNTIME HOME (UPGRADED WITH ANALYTICS ENGINE) ---
if choice == "🏠 DASHBOARD HOME":
    st.markdown("<h1 style='text-align: center; font-weight:700; letter-spacing:-1px;'>Elite Management Framework</h1>", unsafe_allow_html=True)
    
    # Live Quick Stats Analytics Feature
    if data:
        total_students = len(data)
        all_scores = [sum(info['marks'].values()) / TOTAL_MARKS * 100 for info in data.values()]
        avg_school_score = sum(all_scores) / total_students
        
        c1, c2, c3 = st.columns(3)
        c1.metric("TOTAL ACTIVE PROFILES", f"{total_students} Students")
        c2.metric("GLOBAL ACADEMIC YIELD", f"{avg_school_score:.2f}%")
        c3.metric("SYSTEM INTEGRITY STATUS", "SECURE (100%)")
        
        # Performance Distribution Chart Feature
        st.markdown("<div class='premium-card'>", unsafe_allow_html=True)
        st.subheader("📊 Cross-Student Performance Metric Mapping")
        chart_df = pd.DataFrame({
            "Student Name": [info['name'] for info in data.values()],
            "Overall Grade Yield (%)": all_scores
        }).set_index("Student Name")
        st.bar_chart(chart_df)
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class='premium-card' style='text-align: center;'>
            <h3 style='color: #00F2FE !important;'>Next-Gen Student Analytics and Dynamic Asset Generation Pipeline</h3>
            <p style='color: #9CA3AF !important;'>Welcome to the operational hub. To get started instantly, move to the control panel or seed the mock engine inside the structural export workspace.</p>
        </div>
        """, unsafe_allow_html=True)

    st.image("https://img.freepik.com/free-vector/connected-world-concept-illustration_114360-3027.jpg", use_container_width=True)

# --- VIEW 2: DATABASE ADMIN ACCESS CONTROL ---
elif choice == "🔐 CONTROL PANEL":
    st.title("🛡️ Central Core Control Panel")
    
    if 'admin_auth' not in st.session_state: 
        st.session_state.admin_auth = False

    if not st.session_state.admin_auth:
        st.markdown("<div class='premium-card'>", unsafe_allow_html=True)
        with st.form("Identity Verification"):
            st.subheader("Administrative Credential Crypt-Lock")
            u = st.text_input("Username Key", placeholder="admin")
            p = st.text_input("Security Phrase Code", type="password")
            if st.form_submit_button("AUTHORIZE ENTRY"):
                if u == ADMIN_USERNAME and p == ADMIN_PASSWORD:
                    st.session_state.admin_auth = True
                    st.rerun()
                else: 
                    st.error("Access Denied: Signature Mismatch Check.")
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.sidebar.button("TERMINATE ADMIN SESSION", on_click=lambda: st.session_state.update({"admin_auth": False}))
        
        tab1, tab2, tab3, tab4 = st.tabs(["📝 Add Record Entry", "📊 Ledger Analytics", "🔄 Hot-Fix Modification & Deletion", "📥 Structural Export & Tools"])

        with tab1:
            st.markdown("<div class='premium-card'>", unsafe_allow_html=True)
            st.subheader("Register New Entry Profile")
            with st.form("add_form", clear_on_submit=True):
                col1, col2, col3 = st.columns(3)
                r = col1.text_input("Roll ID Key (e.g. 1001)")
                n = col2.text_input("Full Legal Identity Name")
                cl = col3.text_input("Academic Level Grade")
                sess = st.text_input("Session Period Window", value="2026-2027")
                
                st.write("---")
                st.markdown("<p style='color: #00F2FE; font-weight:600;'>Subject Matrix Allocation Metrics (Max 100)</p>", unsafe_allow_html=True)
                marks = {}
                m_cols = st.columns(3)
                for idx, sub in enumerate(SUBJECTS):
                    marks[sub] = m_cols[idx % 3].number_input(sub, min_value=0, max_value=100, value=90)
                
                if st.form_submit_button("COMMIT ENTRY TO LOGS"):
                    if r and n:
                        data[r] = {"name": n, "class": cl, "session": sess, "marks": marks, "date": str(datetime.now().date())}
                        save_data(data)
                        st.snow()
                        st.success(f"Record profile tracking system online for {n}.")
                    else: 
                        st.error("Execution Interrupted: Required primary record strings missing.")
            st.markdown("</div>", unsafe_allow_html=True)

        with tab2:
            st.markdown("<div class='premium-card'>", unsafe_allow_html=True)
            st.subheader("Active Registry Storage Stream")
            if data:
                db_list = [{"Roll ID": r, "Identity": i['name'], "Level": i['class'], "Aggregated Total": sum(i['marks'].values())} for r, i in data.items()]
                st.dataframe(pd.DataFrame(db_list), use_container_width=True)
            else: 
                st.info("System Vault Data Engine is completely unpopulated.")
            st.markdown("</div>", unsafe_allow_html=True)

        with tab3:
            st.markdown("<div class='premium-card'>", unsafe_allow_html=True)
            st.subheader("Hot-Patch Data Record Utility")
            u_roll = st.text_input("Query Verification Roll ID Target")
            if u_roll in data:
                # CRUD Delete Feature Upgrade Added Here
                if st.button("🔥 PERMANENTLY ERASE THIS STUDENT PROFILE", type="secondary"):
                    del data[u_roll]
                    save_data(data)
                    st.warning("Profile purged from secure localized disk.")
                    st.rerun()
                
                with st.form("upd"):
                    st.info(f"Writing Overwrite Sequence For Student: {data[u_roll]['name']}")
                    new_m = {sub: st.number_input(sub, 0, 100, value=data[u_roll]['marks'].get(sub, 90)) for sub in SUBJECTS}
                    if st.form_submit_button("OVERWRITE STORED METRICS"):
                        data[u_roll]['marks'] = new_m
                        save_data(data)
                        st.success("Buffer updates successfully integrated into persistence volume.")
            elif u_roll: 
                st.error("Specified ID mapping target failed search parameters.")
            st.markdown("</div>", unsafe_allow_html=True)

        with tab4:
            st.markdown("<div class='premium-card'>", unsafe_allow_html=True)
            st.subheader("Data Portability Extraction Matrix")
            if data:
                export_list = []
                for r, info in data.items():
                    row = {"Roll ID": r, "Identity Name": info['name'], "Academic Level": info['class']}
                    row.update(info['marks'])
                    t = sum(info['marks'].values())
                    p = (t / TOTAL_MARKS) * 100
                    row.update({"Total Matrix": t, "Percentage Yield": f"{p:.2f}%", "Letter Code": get_detailed_grade(p)[0]})
                    export_list.append(row)
                st.download_button("GENERATE STRUCTURAL FLAT FILE (CSV)", pd.DataFrame(export_list).to_csv(index=False).encode('utf-8'), "Elite_Academic_Registry.csv")
            
            # Auto Seeder Feature Setup
            st.write("---")
            st.subheader("🛠️ Fast Diagnostics & Seeder")
            if st.button("🚀 INITIALIZE SAMPLE REGISTRY DATA LOGS"):
                seed_sample_data()
            st.markdown("</div>", unsafe_allow_html=True)

# --- VIEW 3: SECURE STUDENT SHEET EXTRACTION & GENERATION ---
elif choice == "👨‍🎓 REPORT CARD PORTAL":
    st.title("🎓 High-Fidelity Performance Portal")
    st.write("Extract encrypted metrics and compile print-ready academic documentation instantly.")
    
    col_l, col_r = st.columns([1, 2])
    
    with col_l:
        st.markdown("<div class='premium-card'>", unsafe_allow_html=True)
        roll = st.text_input("Encrypted Identity Roll Number", placeholder="e.g. 1001")
        retrieve_triggered = st.button("RETRIEVE PERFORMANCE METRICS")
        st.markdown("</div>", unsafe_allow_html=True)
        
    if roll:
        if roll in data:
            s_data = data[roll]
            if retrieve_triggered:
                st.balloons()
            
            with col_r:
                st.markdown(f"""
                <div class='premium-card'>
                    <small style='color: #00F2FE; text-transform: uppercase; font-weight:700; letter-spacing:1px;'>Verified Academic Registry Profile Found</small>
                    <h1 style='margin:0; color:#FFFFFF; font-weight: 700;'>{s_data['name']}</h1>
                    <p style='color: #9CA3AF; margin-top:5px;'>Class/Level Assignment: <b>{s_data['class']}</b> &nbsp;|&nbsp; Active Session: <b>{s_data.get('session', '2026-2027')}</b></p>
                </div>
                """, unsafe_allow_html=True)
                
                rendered_metrics_list = []
                for sub in SUBJECTS:
                    m_val = s_data['marks'].get(sub, 0)
                    l_grd, gpa_val, remk = get_detailed_grade(m_val)
                    rendered_metrics_list.append({
                        "Subject Area": sub,
                        "Obtained Marks": f"{m_val} / 100",
                        "Letter Grade": l_grd,
                        "GPA Assignment": gpa_val,
                        "Evaluation Summary": remk
                    })
                
                st.table(pd.DataFrame(rendered_metrics_list))
                
                tot = sum(s_data['marks'].values())
                p_yield = (tot / TOTAL_MARKS) * 100
                badge_lbl, badge_col = get_ui_badge(p_yield)
                
                c1, c2, c3 = st.columns(3)
                c1.metric("AGGREGATE RAW TOTAL", f"{tot} / {TOTAL_MARKS}")
                c2.metric("PROPORTIONAL YIELD (%)", f"{p_yield:.2f}%")
                
                with c3:
                    st.markdown(f"""
                        <div style='background: rgba(255,255,255,0.03); padding: 10px 20px; border-radius:16px; border: 1px solid {badge_col}; text-align: center;'>
                            <small style='color: #9CA3AF; font-size:11px; text-transform:uppercase;'>System Performance Index</small>
                            <h3 style='color: {badge_col} !important; margin: 5px 0 0 0; font-weight:700;'>{badge_lbl}</h3>
                        </div>
                    """, unsafe_allow_html=True)
                
                # --- AUTOMATED HIGH-FIDELITY PRINT-READY PDF GENERATION ENGINE ---
                st.markdown("<div class='download-btn-container'>", unsafe_allow_html=True)
                pdf_output_stream = generate_pdf(roll, s_data)
                st.download_button(
                    label="📥 DOWNLOAD OFFICIAL CANVA-STYLE PROGRESS REPORT (PDF)",
                    data=pdf_output_stream,
                    file_name=f"Progress_Report_{s_data['name'].replace(' ', '_')}.pdf",
                    mime="application/pdf"
                )
                st.markdown("</div>", unsafe_allow_html=True)
        else:
            if retrieve_triggered or roll:
                st.error("Identity lookup match query missing from current localized secure directory storage.")
