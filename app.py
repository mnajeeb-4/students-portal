import streamlit as st
import json
import os
import base64
import pandas as pd
from datetime import datetime
import io
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import Table, TableStyle

# ------ PLOTLY IMPORT ------
PLOTLY_AVAILABLE = False
try:
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except Exception:
    PLOTLY_AVAILABLE = False

# ---------- CONFIGURATION ----------
FILE_NAME = "students.json"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "1234"
SUBJECTS = ["English", "Urdu", "Math", "Science", "Sindhi", "Islamiyat", "Social Studies"]
TOTAL_MARKS = 700

# ---------- PREMIUM UI CONFIG (KINETIC TYPOGRAPHY OVERHAUL) ----------
st.set_page_config(page_title="Elite Academy", page_icon="📘", layout="wide")

if 'dark_theme' not in st.session_state:
    st.session_state.dark_theme = True

# UI DESIGN SKIN - KINETIC TYPOGRAPHY (Colors unchanged for toggle logic)
theme_bg = "#09090B" if st.session_state.dark_theme else "#FAFAFA"
text_color = "#FAFAFA" if st.session_state.dark_theme else "#09090B"
input_border = "#3F3F46" if st.session_state.dark_theme else "#A1A1AA"
card_bg = "#09090B" if st.session_state.dark_theme else "#FAFAFA"
shadow_color = "none"

st.markdown(f"""
<style>
    /* IMPORT KINETIC TYPOGRAPHY FONTS */
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700&display=swap');
    
    /* GLOBAL RESET */
    .stApp, .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp p, .stApp li, .stApp span:not(.brand-text) {{
        color: {text_color} !important;
        font-family: 'Space Grotesk', sans-serif !important;
    }}
    .brand-text {{ color: #DFE104 !important; }}
    
    .stApp {{
        background: {theme_bg} !important;
        background-size: auto !important;
        animation: none !important;
    }}

    /* SIDEBAR - FLAT BRUTALIST */
    [data-testid="stSidebar"] {{
        background: {theme_bg} !important;
        backdrop-filter: none !important;
        border-right: 2px solid {input_border} !important;
    }}

    /* INPUTS - OVERSIZED UNDERLINE */
    div[data-testid="stTextInput"] input, div[data-testid="stNumberInput"] input {{
        background: transparent !important;
        border: none !important;
        border-bottom: 2px solid {input_border} !important;
        border-radius: 0px !important;
        padding: 0.75rem 0 !important;
        color: {text_color} !important;
        font-family: 'Space Grotesk', sans-serif !important;
        text-transform: uppercase !important;
        font-weight: 700 !important;
        font-size: 1.25rem !important;
        letter-spacing: -0.02em !important;
        backdrop-filter: none !important;
        box-shadow: none !important;
    }}
    div[data-testid="stTextInput"] input:focus, div[data-testid="stNumberInput"] input:focus {{
        border-bottom-color: #DFE104 !important;
        box-shadow: none !important;
    }}
    div[data-testid="stTextInput"] label {{
        color: #A1A1AA !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
        font-weight: 700 !important;
        font-size: 0.75rem !important;
    }}

    /* BUTTONS - ACCENT YELLOW, ROUNDED NONE */
    div.stButton > button {{
        background: #DFE104 !important;
        color: #09090B !important;
        border-radius: 0px !important;
        border: none !important;
        padding: 16px 32px !important;
        font-family: 'Space Grotesk', sans-serif !important;
        text-transform: uppercase !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em !important;
        box-shadow: none !important;
        transition: transform 0.2s ease !important;
        width: 100%;
        height: 56px !important;
    }}
    div.stButton > button:hover {{ transform: scale(1.05) !important; }}

    /* CARDS - FLAT, SHARP BORDERS, NO SHADOWS */
    .premium-glass-card {{
        background: {card_bg} !important;
        border: 2px solid {input_border} !important;
        border-radius: 0px !important;
        backdrop-filter: none !important;
        box-shadow: none !important;
        padding: 48px 32px !important;
        transition: all 0.3s ease !important;
    }}
    .premium-glass-card:hover {{
        background: #DFE104 !important;
        border-color: #DFE104 !important;
        transform: none !important;
    }}
    .premium-glass-card:hover * {{
        color: #09090B !important; /* INVERT TEXT ON HOVER */
    }}

    /* METRICS - MUTED BACKGROUND */
    .metric-card {{
        background: #27272A !important;
        border: none !important;
        border-radius: 0px !important;
        padding: 24px !important;
        text-align: center;
        transition: all 0.3s ease !important;
    }}
    .metric-card:hover {{
        background: #DFE104 !important;
    }}
    .metric-card:hover * {{ color: #09090B !important; }}
    .metric-card h3 {{ color: #A1A1AA !important; font-size: 0.75rem !important; letter-spacing: 0.05em !important; text-transform: uppercase !important; }}
    .metric-card h2 {{ color: #FAFAFA !important; font-size: 3rem !important; font-weight: 700 !important; }}

    /* ALERTS - BRUTALIST STRIPES */
    .alert-box {{
        background: #27272A !important;
        border-radius: 0px !important;
        border-left: 4px solid #DFE104 !important;
        color: #FAFAFA !important;
        padding: 16px 20px !important;
        animation: slideIn 0.5s ease;
    }}
    .alert-box.error {{ border-left-color: #E74C3C !important; }}
    .alert-box.info {{ border-left-color: #3498DB !important; }}
    @keyframes slideIn {{ from {{ opacity:0; transform:translateY(-10px); }} to {{ opacity:1; transform:translateY(0); }} }}

    /* DATAFRAMES - 2PX BORDERS */
    .stDataFrame {{
        background: transparent !important;
    }}
    .stDataFrame table {{
        border: 2px solid {input_border} !important;
        border-radius: 0px !important;
        background: {theme_bg} !important;
    }}
    .stDataFrame th {{
        background: #27272A !important;
        color: #FAFAFA !important;
        text-transform: uppercase !important;
        font-family: 'Space Grotesk', sans-serif !important;
        border: none !important;
    }}
    .stDataFrame td {{
        color: #FAFAFA !important;
        border-bottom: 1px solid {input_border} !important;
    }}
</style>
""", unsafe_allow_html=True)

# ---------- HELPERS ----------
def load_data():
    if os.path.exists(FILE_NAME):
        try:
            with open(FILE_NAME, "r") as file:
                return json.load(file)
        except: return {}
    return {}

def save_data(data):
    with open(FILE_NAME, "w") as file:
        json.dump(data, file, indent=4)

def get_grade_gpa(percentage):
    if percentage >= 93: return "A+", "4.0/4.0", "93% to 100%"
    elif percentage >= 90: return "A", "3.7/4.0", "90% to 92%"
    elif percentage >= 87: return "B+", "3.3/4.0", "87% to 89%"
    elif percentage >= 83: return "B", "3.0/4.0", "83% to 86%"
    elif percentage >= 80: return "B-", "2.7/4.0", "80% to 82%"
    elif percentage >= 77: return "C+", "2.3/4.0", "77% to 79%"
    elif percentage >= 73: return "C", "2.0/4.0", "73% to 76%"
    elif percentage >= 70: return "C-", "1.7/4.0", "70% to 72%"
    elif percentage >= 67: return "D+", "1.3/4.0", "67% to 69%"
    elif percentage >= 63: return "D", "1.0/4.0", "63% to 66%"
    elif percentage >= 60: return "D-", "0.7/4.0", "60% to 62%"
    else: return "F", "0.0/4.0", "0% to 59%"

# ---------- PDF GENERATION (UNTOUCHED) ----------
def generate_pdf_report(roll, name, cls, marks_dict, date_today, profile_pic_base64=None):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    brown_dark = colors.HexColor('#604227')
    brown_brand = colors.HexColor('#7a4c34')
    red_brand = colors.HexColor('#c83c2f')
    cream_bg = colors.HexColor('#f5f0e6')
    cream_light = colors.HexColor('#eae2d7')
    
    c.setFillColor(cream_bg)
    c.rect(0, 0, width, height, fill=1, stroke=0)
    
    c.setFillColor(colors.HexColor('#e0d7c8'))
    c.circle(70, height - 60, 50, stroke=0, fill=1)
    c.setFillColor(colors.HexColor('#d4c8b6'))
    c.circle(width - 70, height - 150, 80, stroke=0, fill=1)
    c.setFillColor(colors.HexColor('#c83c2f'))
    c.setFillAlpha(0.1)
    c.circle(145, height - 80, 45, stroke=0, fill=1)
    c.setFillAlpha(1)

    if profile_pic_base64:
        try:
            img_bytes = base64.b64decode(profile_pic_base64)
            img_buffer = io.BytesIO(img_bytes)
            c.setFillColor(colors.HexColor('#7a4c34'))
            c.circle(100, height - 110, 55, stroke=0, fill=1)
            c.drawImage(img_buffer, 55, height - 155, width=90, height=90, mask='auto')
        except Exception:
            pass

    c.setFillColor(brown_brand)
    c.roundRect((width - 250) / 2, height - 90, 250, 55, 10, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(width/2, height - 65, "Progress Report")
    c.setFillColor(brown_brand)
    c.setFont("Helvetica", 12)
    c.drawCentredString(width/2, height - 120, "Anderson Family Homeschool")

    x_margin = 50
    info_y = height - 160
    c.setFillColor(red_brand)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(x_margin, info_y, "Student Name:")
    c.drawString(x_margin, info_y - 35, "Grade:")
    c.drawString(x_margin + 300, info_y, "School Year:")
    c.drawString(x_margin + 300, info_y - 35, "Teacher:")
    c.setStrokeColor(colors.grey)
    c.setLineWidth(0.8)
    c.line(x_margin, info_y - 10, x_margin + 250, info_y - 10)
    c.line(x_margin, info_y - 45, x_margin + 250, info_y - 45)
    c.line(x_margin + 300, info_y - 10, x_margin + 520, info_y - 10)
    c.line(x_margin + 300, info_y - 45, x_margin + 520, info_y - 45)
    c.setFillColor(brown_dark)
    c.setFont("Helvetica", 12)
    c.drawString(x_margin + 5, info_y - 15, name)
    c.drawString(x_margin + 5, info_y - 50, cls)
    c.drawString(x_margin + 305, info_y - 15, date_today)
    c.drawString(x_margin + 305, info_y - 50, "Faculty (Auto-Generated)")

    table_y = height - 240
    table_data = [["Course Title", "No. of Units", "Course Grade", "Teacher's Remarks"]]
    for subject in SUBJECTS:
        mark = marks_dict.get(subject, 0)
        perc_sub = (mark / 100) * 100 if mark else 0 
        grade, _, _ = get_grade_gpa(perc_sub)
        remark = "Excellent" if perc_sub>=90 else "Good" if perc_sub>=80 else "Satisfactory" if perc_sub>=70 else "Needs Improvement"
        table_data.append([subject, "1", grade, remark])

    t = Table(table_data, colWidths=[220, 75, 75, 110])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), brown_brand),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
    ]))
    w, h = t.wrap(0, 0)
    t.drawOn(c, x_margin, table_y - h)

    current_y = table_y - h - 40
    key_h = 110
    c.setFillColor(brown_brand)
    c.rect(x_margin, current_y - key_h, 130, key_h, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(x_margin + 65, current_y - key_h + 55, "GRADING")
    c.drawCentredString(x_margin + 65, current_y - key_h + 40, "KEY")
    
    c.setFillColor(cream_light)
    c.setFillAlpha(0.8)
    c.rect(x_margin + 130, current_y - key_h, 365, key_h, fill=1, stroke=0)
    c.setFillAlpha(1)
    c.setFillColor(brown_dark)
    c.setFont("Helvetica", 8)
    g_y = current_y - key_h + 95
    c.drawString(x_margin + 140, g_y, "A+ = 93% to 100% | 4.0/4.0")
    c.drawString(x_margin + 140, g_y - 12, "A = 90% to 92% | 3.7/4.0")
    c.drawString(x_margin + 140, g_y - 24, "B+ = 87% to 89% | 3.3/4.0")
    c.drawString(x_margin + 140, g_y - 36, "B  = 83% to 86% | 3.0/4.0")
    c.drawString(x_margin + 140, g_y - 48, "B- = 80% to 82% | 2.7/4.0")
    c.drawString(x_margin + 140, g_y - 60, "C+ = 77% to 79% | 2.3/4.0")
    c.drawString(x_margin + 140, g_y - 72, "C  = 73% to 76% | 2.0/4.0")
    c.drawString(x_margin + 280, g_y, "C- = 70% to 72% | 1.7/4.0")
    c.drawString(x_margin + 280, g_y - 12, "D+ = 67% to 69% | 1.3/4.0")
    c.drawString(x_margin + 280, g_y - 24, "D  = 63% to 66% | 1.0/4.0")
    c.drawString(x_margin + 280, g_y - 36, "D- = 60% to 62% | 0.7/4.0")
    c.drawString(x_margin + 280, g_y - 48, "F  = 0% to 59% | 0.0/4.0")
    c.drawString(x_margin + 280, g_y - 60, "I  = Incomplete")

    footer_y = 0
    c.setFillColor(brown_brand)
    c.rect(0, footer_y, width, 45, fill=1, stroke=0)
    quarters = ["Quarter One", "Quarter Two", "Quarter Three", "Quarter Four"]
    for i, q in enumerate(quarters):
        box_x = 40 + (i * 125)
        c.setFillColor(colors.white)
        c.rect(box_x, 10, 110, 25, fill=1, stroke=0)
        c.setFillColor(brown_brand)
        c.setFont("Helvetica", 9)
        c.drawCentredString(box_x + 55, 25, q)

    c.save()
    buffer.seek(0)
    return buffer

# ---------- DATA ----------
data = load_data()
if 'admin_auth' not in st.session_state: st.session_state.admin_auth = False

# ---------- SIDEBAR ----------
with st.sidebar:
    st.markdown("<h3 style='text-align:center; color:#DFE104; text-transform:uppercase; letter-spacing:-0.02em;'>📘 ELITE</h3>", unsafe_allow_html=True)
    st.markdown("<hr style='border-top: 2px solid #3F3F46;'>", unsafe_allow_html=True)
    st.session_state.dark_theme = st.toggle("🌙 Dark Mode", value=st.session_state.dark_theme)
    choice = st.radio("Navigation", ["🏠 Home", "🛡️ Admin Panel", "📋 Student Result"])
    st.markdown(f"<p style='font-size:12px; opacity:0.6; text-transform:uppercase;'>Active Students: <b>{len(data)}</b></p>", unsafe_allow_html=True)

# ---------- PAGE 1: HOME ----------
if choice == "🏠 Home":
    st.markdown("<h1 style='font-family:Space Grotesk; text-transform:uppercase; letter-spacing:-0.02em;'>Anderson Family <br><span class='brand-text'>Homeschool Management</span></h1>", unsafe_allow_html=True)
    st.markdown("<div class='premium-glass-card'><h4 style='text-transform:uppercase;'>🚀 Next-Gen Portal</h4>Premium Kinetic Typography UI with integrated Profile Picture & Report Generation.</div>", unsafe_allow_html=True)

# ---------- PAGE 2: ADMIN (UNTOUCHED LOGIC) ----------
elif choice == "🛡️ Admin Panel":
    if not st.session_state.admin_auth:
        with st.form("admin_login"):
            st.markdown("<div class='premium-glass-card'>", unsafe_allow_html=True)
            u = st.text_input("Username", placeholder="admin")
            p = st.text_input("Password", type="password", placeholder="****")
            if st.form_submit_button("Unseal Access"):
                if u == ADMIN_USERNAME and p == ADMIN_PASSWORD:
                    st.session_state.admin_auth = True
                    st.rerun()
                else: st.markdown("<div class='alert-box error'>🔒 Invalid Credentials</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.sidebar.button("🚪 Logout", on_click=lambda: st.session_state.update({"admin_auth": False}))
        st.subheader("📊 Executive Dashboard")
        
        if data:
            totals = [sum(i['marks'].values()) for i in data.values()]
            c1, c2, c3 = st.columns(3)
            c1.markdown(f"<div class='metric-card'><h3>Total Students</h3><h2>{len(data)}</h2></div>", unsafe_allow_html=True)
            c2.markdown(f"<div class='metric-card'><h3>Avg Performance</h3><h2>{sum(totals)/len(totals)/7:.1f}%</h2></div>", unsafe_allow_html=True)
            top_student = max(data.items(), key=lambda x: sum(x[1]['marks'].values()))
            c3.markdown(f"<div class='metric-card'><h3>🏆 Top Scorer</h3><h2>{top_student[1]['name']}</h2></div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='alert-box info'>📂 Database is empty. Add your first student below!</div>", unsafe_allow_html=True)

        tab1, tab2, tab3, tab4 = st.tabs(["📝 Add Student", "📂 Search Database", "📥 Data Export", "📄 Backup JSON"])
        
        with tab1:
            with st.form("add_student"):
                r = st.text_input("Roll Number")
                n = st.text_input("Student Name")
                cl = st.text_input("Class")
                marks = {}
                cols = st.columns(3)
                for i, sub in enumerate(SUBJECTS):
                    marks[sub] = cols[i%3].number_input(sub, 0, 100)
                
                if st.form_submit_button("Add Record"):
                    if r and n:
                        data[r] = {"name": n, "class": cl, "marks": marks, "date": str(datetime.now().date())}
                        save_data(data)
                        st.markdown("<div class='alert-box'>✅ Record Saved!</div>", unsafe_allow_html=True)
                        st.rerun()
                    else: st.markdown("<div class='alert-box error'>❌ Roll and Name mandatory</div>", unsafe_allow_html=True)
        
        with tab2:
            search_query = st.text_input("🔍 Search by Roll or Name")
            if data:
                df_data = []
                for r, info in data.items():
                    if search_query.lower() in r.lower() or search_query.lower() in info['name'].lower():
                        t = sum(info['marks'].values())
                        p = (t/TOTAL_MARKS)*100
                        g, _, _ = get_grade_gpa(p)
                        df_data.append({"Roll": r, "Name": info['name'], "Class": info['class'], "Total": t, "Grade": g})
                if df_data:
                    st.dataframe(pd.DataFrame(df_data), use_container_width=True)
                else: st.info("No matching records.")
            else: st.info("Database is empty.")
        
        with tab3:
            if data:
                export_list = []
                for r, info in data.items():
                    row = {"Roll": r, "Name": info['name'], "Class": info['class']}
                    row.update(info['marks'])
                    t = sum(info['marks'].values())
                    p = (t/TOTAL_MARKS)*100
                    g, gpa, _ = get_grade_gpa(p)
                    row.update({"Total": t, "%": f"{p:.1f}", "Grade": g, "GPA": gpa})
                    export_list.append(row)
                csv = pd.DataFrame(export_list).to_csv(index=False).encode('utf-8')
                st.download_button("📥 Download Full CSV", data=csv, file_name="Elite_Export.csv")
        
        with tab4:
            if data:
                json_data = json.dumps(data, indent=4).encode('utf-8')
                st.download_button("📥 Download JSON Backup", data=json_data, file_name="students_backup.json")

# ---------- PAGE 3: STUDENT RESULT (KINETIC TYPOGRAPHY HTML CARD) ----------
elif choice == "📋 Student Result":
    
    if 'card_generated' not in st.session_state: st.session_state.card_generated = False
    if 'current_roll' not in st.session_state: st.session_state.current_roll = None
    if 'current_student_data' not in st.session_state: st.session_state.current_student_data = None
    if 'temp_pic' not in st.session_state: st.session_state.temp_pic = None

    st.subheader("📋 Student Result Portal")
    with st.container():
        st.markdown("<div class='premium-glass-card'>", unsafe_allow_html=True)
        
        default_roll = st.session_state.current_roll if st.session_state.current_roll else ""
        roll = st.text_input("Enter your Roll Number", value=default_roll, placeholder="e.g. 1001")
        
        if st.button("🔍 Generate Report"):
            if roll in data:
                st.session_state.current_roll = roll
                st.session_state.current_student_data = data[roll]
                st.session_state.card_generated = True
                st.rerun()
            else:
                st.markdown("<div class='alert-box error'>❌ Roll number not found!</div>", unsafe_allow_html=True)
                st.session_state.card_generated = False

        if st.session_state.card_generated and st.session_state.current_student_data:
            s = st.session_state.current_student_data
            total = sum(s['marks'].values())
            perc = (total/TOTAL_MARKS)*100
            grade, gpa, _ = get_grade_gpa(perc)
            
            st.markdown("### 📸 Profile Picture")
            current_pic = s.get('profile_pic', None)
            if st.session_state.temp_pic:
                current_pic = st.session_state.temp_pic
            
            col_pic1, col_pic2 = st.columns([1, 2])
            with col_pic1:
                if current_pic:
                    st.image(f"data:image/jpeg;base64,{current_pic}", width=150, caption="Current Photo")
            
            with col_pic2:
                img_file = st.camera_input("Take a picture (or upload below)", key="pic_cam_1")
                if img_file is None:
                    img_file = st.file_uploader("Upload a photo instead", type=['jpg', 'jpeg', 'png'], key="pic_upload_1")
                
                if st.button("💾 Update Profile Picture"):
                    if img_file is not None:
                        import base64
                        bytes_data = img_file.getvalue()
                        base64_str = base64.b64encode(bytes_data).decode('utf-8')
                        s['profile_pic'] = base64_str
                        data[st.session_state.current_roll] = s
                        save_data(data)
                        st.session_state.temp_pic = base64_str
                        st.success("✅ Profile picture updated successfully! Page state preserved.")
                        st.rerun()
                    else:
                        st.warning("Please take or upload a picture first.")

            # =====================================================================
            # 1. REDESIGNED HTML CARD (KINETIC TYPOGRAPHY / BRUTALIST)
            # =====================================================================
            img_html = ""
            if current_pic:
                img_html = f'<img src="data:image/jpeg;base64,{current_pic}" style="width:90px;height:90px;border-radius:0px;border:2px solid #DFE104;position:absolute;top:20px;right:20px;z-index:2;object-fit:cover;" />'

            html_content = f"""
            <div style="position: relative; background: #09090B; border: 2px solid #3F3F46; padding: 40px 32px; margin-bottom: 20px; overflow: hidden; color: #FAFAFA; font-family: 'Space Grotesk', sans-serif; box-shadow: none; min-height: 400px;">
                <div style="position: absolute; top: -30px; left: -20px; width: 140px; height: 140px; background: #27272A; border-radius: 50%; z-index: 0; opacity: 0.5;"></div>
                <div style="position: absolute; top: -80px; right: -40px; width: 200px; height: 200px; background: #27272A; border-radius: 50%; z-index: 0; opacity: 0.5;"></div>
                
                {img_html}
                
                <div style="position: relative; z-index: 1; background: #DFE104; width: 100%; max-width: 280px; margin: 0 auto; border-radius: 0px; padding: 16px 0; text-align: center;">
                    <h3 style="color: #09090B; font-weight: 700; margin: 0; text-transform: uppercase; letter-spacing: -0.02em;">Progress Report</h3>
                </div>
                <h5 style="position: relative; z-index: 1; color: #A1A1AA; text-align: center; margin-top: 16px; font-weight: 400; text-transform: uppercase; letter-spacing: 0.05em;">Anderson Family Homeschool</h5>

                <div style="position: relative; z-index: 1; display: grid; grid-template-columns: 1fr 1fr; gap: 24px; margin-top: 32px;">
                    <div><label style="color: #A1A1AA; text-transform: uppercase; font-weight: 700; font-size: 12px; letter-spacing: 0.05em;">Student Name:</label><div style="border-bottom: 2px solid #3F3F46; padding: 8px 0; color: #FAFAFA; font-size: 1.25rem; text-transform: uppercase; letter-spacing: -0.02em; font-weight: 700;">{s['name']}</div></div>
                    <div><label style="color: #A1A1AA; text-transform: uppercase; font-weight: 700; font-size: 12px; letter-spacing: 0.05em;">School Year:</label><div style="border-bottom: 2px solid #3F3F46; padding: 8px 0; color: #FAFAFA; font-size: 1.25rem; text-transform: uppercase; letter-spacing: -0.02em; font-weight: 700;">{datetime.now().strftime('%Y-%m-%d')}</div></div>
                    <div><label style="color: #A1A1AA; text-transform: uppercase; font-weight: 700; font-size: 12px; letter-spacing: 0.05em;">Grade:</label><div style="border-bottom: 2px solid #3F3F46; padding: 8px 0; color: #FAFAFA; font-size: 1.25rem; text-transform: uppercase; letter-spacing: -0.02em; font-weight: 700;">{s['class']}</div></div>
                    <div><label style="color: #A1A1AA; text-transform: uppercase; font-weight: 700; font-size: 12px; letter-spacing: 0.05em;">Teacher:</label><div style="border-bottom: 2px solid #3F3F46; padding: 8px 0; color: #FAFAFA; font-size: 1.25rem; text-transform: uppercase; letter-spacing: -0.02em; font-weight: 700;">Faculty (Auto-Generated)</div></div>
                </div>

                <div style="position: relative; z-index: 1; margin-top: 32px; border: 2px solid #3F3F46; border-bottom: none;">
                    <div style="background: #27272A; color: #FAFAFA; padding: 12px 16px; display: flex; justify-content: space-between; font-weight: 700; font-size: 12px; text-transform: uppercase; letter-spacing: 0.05em;">
                        <span style="flex: 2;">Course Title</span>
                        <span style="flex: 1; text-align: center;">No. of Units</span>
                        <span style="flex: 1; text-align: center;">Course Grade</span>
                        <span style="flex: 1.5; text-align: center;">Teacher's Remarks</span>
                    </div>
                    <div style="background: #09090B; border: none;">
            """
            for sub in SUBJECTS:
                mark = s['marks'].get(sub, 0)
                perc_sub = (mark/100)*100
                grade_sub, _, _ = get_grade_gpa(perc_sub)
                remark = "Excellent" if perc_sub>=90 else "Good" if perc_sub>=80 else "Satisfactory" if perc_sub>=70 else "Needs Improvement"
                html_content += f"""
                        <div style="display: flex; justify-content: space-between; padding: 12px 16px; border-bottom: 2px solid #3F3F46;">
                            <span style="flex: 2; color: #FAFAFA; font-weight: 500; text-transform: uppercase;">{sub}</span>
                            <span style="flex: 1; text-align: center; color: #FAFAFA; font-weight: 700;">1</span>
                            <span style="flex: 1; text-align: center; color: #FAFAFA; font-weight: 700;">{grade_sub}</span>
                            <span style="flex: 1.5; text-align: center; color: #A1A1AA; font-weight: 400; text-transform: uppercase; letter-spacing: 0.02em;">{remark}</span>
                        </div>
                """
            html_content += """
                    </div>
                </div>

                <div style="position: relative; z-index: 1; display: flex; margin-top: 24px; border: 2px solid #3F3F46;">
                    <div style="background: #DFE104; color: #09090B; width: 90px; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 14px; border-right: 2px solid #3F3F46; text-align: center; text-transform: uppercase; letter-spacing: -0.02em;">GRADING<br>KEY</div>
                    <div style="flex: 1; padding: 16px; display: grid; grid-template-columns: 1fr 1fr; gap: 4px 16px; font-size: 12px; color: #FAFAFA; text-transform: uppercase;">
                        <div>A+ = 93% to 100% | 4.0/4.0</div><div>C- = 70% to 72% | 1.7/4.0</div>
                        <div>A = 90% to 92% | 3.7/4.0</div><div>D+ = 67% to 69% | 1.3/4.0</div>
                        <div>B+ = 87% to 89% | 3.3/4.0</div><div>D  = 63% to 66% | 1.0/4.0</div>
                        <div>B  = 83% to 86% | 3.0/4.0</div><div>D- = 60% to 62% | 0.7/4.0</div>
                        <div>B- = 80% to 82% | 2.7/4.0</div><div>F  = 0% to 59% | 0.0/4.0</div>
                        <div>C+ = 77% to 79% | 2.3/4.0</div><div>I  = Incomplete</div>
                        <div>C  = 73% to 76% | 2.0/4.0</div><div></div>
                    </div>
                </div>
            """
            html_content += f"""
                <div style="position: relative; z-index: 1; margin-top: 32px; display: flex; justify-content: space-between; border-top: 2px solid #3F3F46; padding-top: 16px;">
                    <span style="font-size: 16px; font-weight: bold; color: #FAFAFA; text-transform: uppercase;">Total: {total} / {TOTAL_MARKS} | {perc:.1f}%</span>
                    <span style="font-size: 16px; font-weight: bold; color: #DFE104; text-transform: uppercase;">Grade: {grade}</span>
                </div>
            </div>
            """
            
            st.markdown(html_content, unsafe_allow_html=True)

            # ---------- 2. DATA TABLE & CHART ----------
            df = pd.DataFrame(list(s['marks'].items()), columns=["Subject", "Marks"])
            df["Percentage"] = (df["Marks"]/100*100).round(1)
            df["Grade"] = df["Percentage"].apply(lambda x: get_grade_gpa(x)[0])
            
            c1, c2 = st.columns([3, 2])
            with c1:
                st.dataframe(df, use_container_width=True)
                st.metric("GPA (4.0 Scale)", gpa)
            
            with c2:
                if PLOTLY_AVAILABLE:
                    try:
                        fig = go.Figure(data=go.Scatterpolar(
                            r=df["Marks"].tolist(),
                            theta=df["Subject"].tolist(),
                            fill='toself',
                            line=dict(color='#DFE104', width=2),
                            marker=dict(color='#DFE104')
                        ))
                        fig.update_layout(
                            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                            showlegend=False,
                            margin=dict(l=20, r=20, t=20, b=20),
                            paper_bgcolor='rgba(0,0,0,0)',
                            plot_bgcolor='rgba(0,0,0,0)',
                            font=dict(color=text_color, family="Space Grotesk")
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    except Exception:
                        st.error("Radar chart rendering failed.")
                else:
                    st.info("📊 Upgrade for interactive Radar Chart! Run `pip install plotly` in your terminal.")
            
            # ---------- 3. WEAKNESS ANALYZER ----------
            st.markdown("### 🧠 Weakness Analyzer")
            sorted_subjects = df.sort_values(by="Marks")
            weak_subjects = sorted_subjects.head(2)
            
            st.markdown("<div class='alert-box info'>💡 Based on your scores, you should focus more on these subjects:</div>", unsafe_allow_html=True)
            for idx, row in weak_subjects.iterrows():
                st.markdown(f"<div style='background: #27272A; padding: 8px 16px; border-left: 4px solid #DFE104; margin-bottom: 8px; border-radius: 0px; color: #FAFAFA; text-transform: uppercase;'>🔴 <b>{row['Subject']}</b> (Marks: {row['Marks']})</div>", unsafe_allow_html=True)

            # ---------- 4. PDF GENERATION ----------
            if st.button("📥 Download Official Progress Report (PDF)"):
                with st.spinner("Generating Premium PDF..."):
                    pdf = generate_pdf_report(roll, s['name'], s['class'], s['marks'], str(datetime.now().date()), s.get('profile_pic', None))
                    st.download_button("✅ Click to Confirm Download", data=pdf, file_name=f"{s['name']}_{roll}_Report.pdf")
        st.markdown("</div>", unsafe_allow_html=True)
