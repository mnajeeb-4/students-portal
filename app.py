import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime
import io
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter

# ------ PLOTLY IMPORT ----------
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

# ---------- PREMIUM UI CONFIG ----------
st.set_page_config(page_title="Elite Academy Suite", page_icon="📘", layout="wide")

if 'dark_theme' not in st.session_state:
    st.session_state.dark_theme = True

# Dynamic CSS
theme_bg = "linear-gradient(135deg, #1a1a2e, #16213e, #0f3460)" if st.session_state.dark_theme else "linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)"
text_color = "#ffffff" if st.session_state.dark_theme else "#1a1a1a"
input_bg = "rgba(255, 255, 255, 0.15)" if st.session_state.dark_theme else "rgba(0, 0, 0, 0.05)"
input_border = "rgba(255, 255, 255, 0.3)" if st.session_state.dark_theme else "rgba(0, 0, 0, 0.1)"
card_bg = "rgba(255, 255, 255, 0.08)" if st.session_state.dark_theme else "rgba(255, 255, 255, 0.6)"
shadow_color = "rgba(0, 0, 0, 0.5)" if st.session_state.dark_theme else "rgba(0, 0, 0, 0.1)"

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&family=Poppins:wght@400;600;700&display=swap');
    
    .stApp, .stApp h1, .stApp h2, .stApp h3, .stApp p, .stApp li, .stApp span:not(.brand-text) {{
        color: {text_color} !important;
        font-family: 'Inter', sans-serif;
    }}
    .brand-text {{ color: #c83c2f !important; }}
    
    .stApp {{
        background: {theme_bg};
        background-size: 400% 400%;
        animation: gradientShift 15s ease infinite;
    }}
    @keyframes gradientShift {{
        0% {{ background-position: 0% 50%; }}
        50% {{ background-position: 100% 50%; }}
        100% {{ background-position: 0% 50%; }}
    }}
    ::-webkit-scrollbar {{ width: 8px; }}
    ::-webkit-scrollbar-track {{ background: rgba(255, 255, 255, 0.05); border-radius: 10px; }}
    ::-webkit-scrollbar-thumb {{ background: #7a4c34; border-radius: 10px; }}

    [data-testid="stSidebar"] {{
        background: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(20px) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }}
    
    div[data-testid="stTextInput"] input, div[data-testid="stNumberInput"] input {{
        background: {input_bg} !important;
        border: 1px solid {input_border} !important;
        border-radius: 12px !important;
        padding: 10px 15px !important;
        backdrop-filter: blur(5px);
        transition: 0.3s ease;
    }}
    div[data-testid="stTextInput"] input:focus, div[data-testid="stNumberInput"] input:focus {{
        border-color: #c83c2f !important;
        box-shadow: 0 0 20px rgba(200, 60, 47, 0.3);
    }}
    
    .premium-glass-card {{
        background: {card_bg};
        backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 24px;
        padding: 25px;
        margin-bottom: 20px;
        box-shadow: 0 10px 40px {shadow_color};
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }}
    .premium-glass-card:hover {{ transform: translateY(-5px); box-shadow: 0 20px 60px {shadow_color}; }}

    div.stButton > button {{
        background: linear-gradient(135deg, #7a4c34 0%, #c83c2f 100%) !important;
        color: white !important;
        border-radius: 50px !important;
        border: 1px solid rgba(255,255,255,0.3) !important;
        padding: 10px 28px !important;
        font-weight: 700 !important;
        font-family: 'Poppins', sans-serif !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 15px rgba(200, 60, 47, 0.4) !important;
        width: 100%;
    }}
    div.stButton > button:hover {{ transform: scale(1.05) !important; box-shadow: 0 8px 30px rgba(200, 60, 47, 0.7) !important; }}

    .metric-card {{
        background: rgba(255,255,255,0.05);
        border-radius: 16px;
        padding: 20px;
        text-align: center;
        border: 1px solid rgba(255,255,255,0.1);
    }}
    .metric-card h3 {{ margin:0; color:#c83c2f; font-size:12px; letter-spacing:2px; text-transform:uppercase; }}
    .metric-card h2 {{ margin:0; font-size:38px; font-weight:700; }}

    .alert-box {{
        padding: 15px;
        border-radius: 12px;
        border-left: 6px solid #2ecc71;
        background: rgba(46, 204, 113, 0.1);
        margin-bottom: 10px;
        animation: slideIn 0.5s ease;
    }}
    .alert-box.error {{ border-left-color: #e74c3c; background: rgba(231, 76, 60, 0.1); }}
    .alert-box.info {{ border-left-color: #3498db; background: rgba(52, 152, 219, 0.1); }}
    @keyframes slideIn {{ from {{ opacity:0; transform:translateY(-10px); }} to {{ opacity:1; transform:translateY(0); }} }}
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
    if percentage >= 93: return "A", "4.0/4.0", "93% to 100%"
    elif percentage >= 90: return "A-", "3.7/4.0", "90% to 92%"
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

# ---------- EXACT CANVA PDF GENERATION ----------
def generate_pdf_report(roll, name, cls, marks_dict, date_today):
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

    c.setFillColor(brown_brand)
    c.roundRect((width - 250) / 2, height - 90, 250, 55, 10, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(width/2, height - 65, "Progress Report")
    c.setFillColor(brown_brand)
    c.setFont("Helvetica", 12)
    c.drawCentredString(width/2, height - 120, "Anderson Family Homeschool")

    x_margin = 50
    c.setFillColor(red_brand)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(x_margin, height - 160, "Student Name:")
    c.drawString(x_margin, height - 195, "Grade:")
    c.drawString(x_margin + 300, height - 160, "School Year:")
    c.drawString(x_margin + 300, height - 195, "Teacher:")
    
    c.setStrokeColor(colors.grey)
    c.setLineWidth(0.8)
    c.line(x_margin, height - 170, x_margin + 250, height - 170)
    c.line(x_margin, height - 205, x_margin + 250, height - 205)
    c.line(x_margin + 300, height - 170, x_margin + 520, height - 170)
    c.line(x_margin + 300, height - 205, x_margin + 520, height - 205)
    
    c.setFillColor(brown_dark)
    c.setFont("Helvetica", 12)
    c.drawString(x_margin + 5, height - 175, name)
    c.drawString(x_margin + 5, height - 210, cls)
    c.drawString(x_margin + 305, height - 175, date_today)
    c.drawString(x_margin + 305, height - 210, "Faculty (Auto-Generated)")

    table_x, table_y, table_w = x_margin, height - 240, 495
    row_h = 22
    
    c.setFillColor(brown_brand)
    c.rect(table_x, table_y, table_w, 30, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(table_x + 10, table_y + 10, "Course Title")
    c.drawString(table_x + 235, table_y + 10, "No. of Units")
    c.drawString(table_x + 315, table_y + 10, "Course Grade")
    c.drawString(table_x + 385, table_y + 10, "Teacher's Remarks")
    
    current_y = table_y - row_h
    for subject in SUBJECTS:
        mark = marks_dict.get(subject, 0)
        perc_sub = (mark / 100) * 100 if mark else 0 
        grade, _, _ = get_grade_gpa(perc_sub)
        remark = "Excellent" if perc_sub>=90 else "Good" if perc_sub>=80 else "Satisfactory" if perc_sub>=70 else "Needs Improvement"
        
        c.setFillColor(colors.white)
        c.setFillAlpha(0.1)
        c.rect(table_x, current_y, table_w, row_h, fill=1, stroke=0)
        c.setFillAlpha(1)
        
        c.setFillColor(red_brand)
        c.setFont("Helvetica", 10)
        c.drawString(table_x + 10, current_y + 6, subject)
        
        c.setFillColor(brown_dark)
        c.drawString(table_x + 260, current_y + 6, "1")
        c.drawString(table_x + 335, current_y + 6, grade)
        c.drawString(table_x + 400, current_y + 6, remark)
        current_y -= row_h
    
    key_x, key_y, key_h = x_margin, current_y - 30, 115
    c.setFillColor(brown_brand)
    c.rect(key_x, key_y, 130, key_h, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(key_x + 65, key_y + 55, "GRADING")
    c.drawCentredString(key_x + 65, key_y + 40, "KEY")
    
    c.setFillColor(cream_light)
    c.setFillAlpha(0.8)
    c.rect(key_x + 130, key_y, 365, key_h, fill=1, stroke=0)
    c.setFillAlpha(1)
    c.setFillColor(brown_dark)
    c.setFont("Helvetica", 8)
    
    g_y = key_y + 95
    c.drawString(key_x + 140, g_y, "A = 93% to 100% | 4.0/4.0")
    c.drawString(key_x + 140, g_y - 12, "A- = 90% to 92% | 3.7/4.0")
    c.drawString(key_x + 140, g_y - 24, "B+ = 87% to 89% | 3.3/4.0")
    c.drawString(key_x + 140, g_y - 36, "B  = 83% to 86% | 3.0/4.0")
    c.drawString(key_x + 140, g_y - 48, "B- = 80% to 82% | 2.7/4.0")
    c.drawString(key_x + 140, g_y - 60, "C+ = 77% to 79% | 2.3/4.0")
    c.drawString(key_x + 140, g_y - 72, "C  = 73% to 76% | 2.0/4.0")
    c.drawString(key_x + 280, g_y,     "C- = 70% to 72% | 1.7/4.0")
    c.drawString(key_x + 280, g_y - 12, "D+ = 67% to 69% | 1.3/4.0")
    c.drawString(key_x + 280, g_y - 24, "D  = 63% to 66% | 1.0/4.0")
    c.drawString(key_x + 280, g_y - 36, "D- = 60% to 62% | 0.7/4.0")
    c.drawString(key_x + 280, g_y - 48, "F  = 0% to 59% | 0.0/4.0")
    c.drawString(key_x + 280, g_y - 60, "I  = Incomplete")

    footer_y, footer_h = 0, 45
    c.setFillColor(brown_brand)
    c.rect(0, footer_y, width, footer_h, fill=1, stroke=0)
    
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
    st.markdown("<h3 style='text-align:center; color:#c83c2f;'>📘 ELITE</h3>", unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)
    st.session_state.dark_theme = st.toggle("🌙 Dark Mode", value=st.session_state.dark_theme)
    choice = st.radio("Navigation", ["🏠 Home", "🛡️ Admin Panel", "📋 Student Result", "📚 Study Plan"])
    st.markdown(f"<p style='font-size:12px; opacity:0.6;'>Active Students: <b>{len(data)}</b></p>", unsafe_allow_html=True)

# ---------- PAGE 1: HOME ----------
if choice == "🏠 Home":
    st.markdown("<h1 style='font-family:Poppins;'>Anderson Family <br><span class='brand-text'>Homeschool Management</span></h1>", unsafe_allow_html=True)
    st.markdown("<div class='premium-glass-card'><h4>🚀 Next-Gen Portal</h4>Complete ecosystem for tracking academic results, daily study plans, and PDF generation.</div>", unsafe_allow_html=True)

# ---------- PAGE 2: ADMIN ----------
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
                        # Ensure Study Plan is initialized for new student
                        data[r] = {
                            "name": n, 
                            "class": cl, 
                            "marks": marks, 
                            "date": str(datetime.now().date()),
                            "study_plan": {
                                "mon": ["", "", "", "", ""],
                                "tue": ["", "", "", "", ""],
                                "wed": ["", "", "", "", ""],
                                "thu": ["", "", "", "", ""],
                                "fri": ["", "", "", "", ""]
                            }
                        }
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

# ---------- PAGE 3: STUDENT RESULT (SINGLE-VARIABLE HTML FORMATTING) ----------
elif choice == "📋 Student Result":
    st.subheader("📋 Student Result Portal")
    with st.container():
        st.markdown("<div class='premium-glass-card'>", unsafe_allow_html=True)
        roll = st.text_input("Enter your Roll Number", placeholder="e.g. 1001")
        
        if st.button("🔍 Generate Report"):
            if roll in data:
                s = data[roll]
                total = sum(s['marks'].values())
                perc = (total/TOTAL_MARKS)*100
                grade, gpa, _ = get_grade_gpa(perc)
                
                # ---------------------------------------------------------
                # 1. BUILD ENTIRE HTML CARD AS ONE VARIABLE (CRASH FIX)
                # ---------------------------------------------------------
                html_content = f"""
                <div style="position: relative; background: #f5f0e6; border-radius: 20px; padding: 30px; margin-bottom: 20px; overflow: hidden; color: #333; font-family: 'Inter', sans-serif; box-shadow: 0 8px 30px rgba(0,0,0,0.2);">
                    <!-- Background Decorative Circles -->
                    <div style="position: absolute; top: -30px; left: -20px; width: 140px; height: 140px; background: #e0d7c8; border-radius: 50%; z-index: 0; opacity: 0.8;"></div>
                    <div style="position: absolute; top: -80px; right: -40px; width: 200px; height: 200px; background: #d4c8b6; border-radius: 50%; z-index: 0; opacity: 0.8;"></div>
                    <div style="position: absolute; top: -20px; left: 100px; width: 90px; height: 90px; background: #e8d6d0; border-radius: 50%; z-index: 0; opacity: 0.8;"></div>
                    
                    <!-- Header -->
                    <div style="position: relative; z-index: 1; background: #7a4c34; width: 100%; max-width: 280px; margin: 0 auto; border-radius: 12px; padding: 15px 0; text-align: center;">
                        <h3 style="color: white; font-weight: 700; margin: 0;">Progress Report</h3>
                    </div>
                    <h5 style="position: relative; z-index: 1; color: #604227; text-align: center; margin-top: 10px; font-weight: 400;">Anderson Family Homeschool</h5>

                    <!-- Student Info Form -->
                    <div style="position: relative; z-index: 1; display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-top: 20px;">
                        <div>
                            <label style="color: #c83c2f; font-weight: 700; font-size: 14px;">Student Name:</label>
                            <div style="border-bottom: 1px solid #777; padding: 5px 0; color: #444;">{s['name']}</div>
                        </div>
                        <div>
                            <label style="color: #c83c2f; font-weight: 700; font-size: 14px;">School Year:</label>
                            <div style="border-bottom: 1px solid #777; padding: 5px 0; color: #444;">{datetime.now().strftime('%Y-%m-%d')}</div>
                        </div>
                        <div>
                            <label style="color: #c83c2f; font-weight: 700; font-size: 14px;">Grade:</label>
                            <div style="border-bottom: 1px solid #777; padding: 5px 0; color: #444;">{s['class']}</div>
                        </div>
                        <div>
                            <label style="color: #c83c2f; font-weight: 700; font-size: 14px;">Teacher:</label>
                            <div style="border-bottom: 1px solid #777; padding: 5px 0; color: #444;">Faculty (Auto-Generated)</div>
                        </div>
                    </div>

                    <!-- Data Table Start -->
                    <div style="position: relative; z-index: 1; margin-top: 25px;">
                        <div style="background: #7a4c34; color: white; padding: 8px 15px; border-top-left-radius: 8px; border-top-right-radius: 8px; display: flex; justify-content: space-between; font-weight: 700; font-size: 14px;">
                            <span style="flex: 2;">Course Title</span>
                            <span style="flex: 1; text-align: center;">No. of Units</span>
                            <span style="flex: 1; text-align: center;">Course Grade</span>
                            <span style="flex: 1.5; text-align: center;">Teacher's Remarks</span>
                        </div>
                        <div style="background: #f5f0e6; border: 1px solid #ccc; border-top: none; border-bottom-left-radius: 8px; border-bottom-right-radius: 8px;">
                """

                # Dynamic Subject Rows (Loop appended to string safely)
                for sub in SUBJECTS:
                    mark = s['marks'].get(sub, 0)
                    perc_sub = (mark/100)*100
                    grade_sub, _, _ = get_grade_gpa(perc_sub)
                    remark = "Excellent" if perc_sub>=90 else "Good" if perc_sub>=80 else "Satisfactory" if perc_sub>=70 else "Needs Improvement"
                    
                    html_content += f"""
                            <div style="display: flex; justify-content: space-between; padding: 6px 15px; border-bottom: 1px solid #e0d7c8;">
                                <span style="flex: 2; color: #c83c2f; font-weight: 500;">{sub}</span>
                                <span style="flex: 1; text-align: center; color: #333;">1</span>
                                <span style="flex: 1; text-align: center; color: #333;">{grade_sub}</span>
                                <span style="flex: 1.5; text-align: center; color: #333;">{remark}</span>
                            </div>
                    """

                # Grading Key
                html_content += """
                        </div>
                    </div>

                    <!-- Grading Key -->
                    <div style="position: relative; z-index: 1; display: flex; margin-top: 20px; background: #eae2d7; border-radius: 8px;">
                        <div style="background: #7a4c34; color: white; width: 90px; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 14px; border-top-left-radius: 8px; border-bottom-left-radius: 8px; text-align: center;">
                            GRADING<br>KEY
                        </div>
                        <div style="flex: 1; padding: 10px 15px; display: grid; grid-template-columns: 1fr 1fr; gap: 2px 15px; font-size: 11px; color: #604227;">
                            <div>A = 93% to 100% | 4.0/4.0</div>
                            <div>C- = 70% to 72% | 1.7/4.0</div>
                            <div>A- = 90% to 92% | 3.7/4.0</div>
                            <div>D+ = 67% to 69% | 1.3/4.0</div>
                            <div>B+ = 87% to 89% | 3.3/4.0</div>
                            <div>D  = 63% to 66% | 1.0/4.0</div>
                            <div>B  = 83% to 86% | 3.0/4.0</div>
                            <div>D- = 60% to 62% | 0.7/4.0</div>
                            <div>B- = 80% to 82% | 2.7/4.0</div>
                            <div>F  = 0% to 59% | 0.0/4.0</div>
                            <div>C+ = 77% to 79% | 2.3/4.0</div>
                            <div>I  = Incomplete</div>
                            <div>C  = 73% to 76% | 2.0/4.0</div>
                            <div></div>
                        </div>
                    </div>
                """

                # Footer (Total + Grade)
                html_content += f"""
                    <div style="position: relative; z-index: 1; margin-top: 20px; display: flex; justify-content: space-between;">
                        <span style="font-size: 12px; font-weight: bold; color: #604227;">Total: {total} / {TOTAL_MARKS} | Percentage: {perc:.1f}%</span>
                        <span style="font-size: 12px; font-weight: bold; color: #c83c2f;">Letter Grade: {grade}</span>
                    </div>
                </div>
                """

                # SINGLE SAFE RENDER - NO RAW HTML TEXT!
                st.markdown(html_content, unsafe_allow_html=True)
                
                # ---------- 2. DATA TABLE AND RADAR CHART ----------
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
                                line=dict(color='#c83c2f', width=2),
                                marker=dict(color='#c83c2f')
                            ))
                            fig.update_layout(
                                polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                                showlegend=False,
                                margin=dict(l=20, r=20, t=20, b=20),
                                paper_bgcolor='rgba(0,0,0,0)',
                                plot_bgcolor='rgba(0,0,0,0)',
                                font=dict(color=text_color)
                            )
                            st.plotly_chart(fig, use_container_width=True)
                        except Exception:
                            st.error("Radar chart rendering failed.")
                    else:
                        st.info("📊 Upgrade for interactive Radar Chart! Run `pip install plotly` in your terminal.")
                
                # ---------- 3. PDF DOWNLOAD ----------
                with st.spinner("Generating Premium PDF..."):
                    pdf = generate_pdf_report(roll, s['name'], s['class'], s['marks'], str(datetime.now().date()))
                    st.download_button("📥 Download Official Progress Report (PDF)", data=pdf, file_name=f"{s['name']}_{roll}_Report.pdf")
                
            else: 
                st.markdown("<div class='alert-box error'>❌ Roll number not found!</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        # ---------- PAGE 4: STUDY PLAN (NEW FEATURE FROM IMAGE) ----------
elif choice == "📚 Study Plan":
    st.subheader("📚 Personalized Study Planner")
    st.markdown("Plan your week like a pro with this Canva-inspired interactive scheduler.", unsafe_allow_html=True)
    
    with st.container():
        st.markdown("<div class='premium-glass-card'>", unsafe_allow_html=True)
        plan_roll = st.text_input("Enter your Roll Number to manage Study Plan", placeholder="e.g. 1001")
        
        if plan_roll and plan_roll in data:
            s = data[plan_roll]
            
            # Initialize study plan if missing (backward compatibility)
            if 'study_plan' not in s:
                s['study_plan'] = {
                    "mon": ["", "", "", "", ""],
                    "tue": ["", "", "", "", ""],
                    "wed": ["", "", "", "", ""],
                    "thu": ["", "", "", "", ""],
                    "fri": ["", "", "", "", ""]
                }
                data[plan_roll] = s
                save_data(data)
            
            # Load current plan
            plan = s['study_plan']
            days = ["mon", "tue", "wed", "thu", "fri"]
            day_labels = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
            
            st.markdown(f"<h4 style='color: #c83c2f;'>Study Plan for: {s['name']}</h4>", unsafe_allow_html=True)
            
            with st.form("study_plan_form"):
                # Create a dynamic grid using columns
                cols = st.columns(6)
                cols[0].markdown("**Time**")
                for i, day in enumerate(day_labels):
                    cols[i+1].markdown(f"**{day}**")
                
                # 5 rows of time slots
                default_times = ["08:00 - 09:00", "09:00 - 10:00", "10:00 - 11:00", "11:00 - 12:00", "12:00 - 13:00"]
                row_inputs = []
                
                for row in range(5):
                    row_cols = st.columns(6)
                    # Time Input
                    time_val = row_cols[0].text_input(f"time_{row}", value=default_times[row], key=f"t_{row}", label_visibility="collapsed")
                    
                    row_data = {"time": time_val}
                    for idx, d in enumerate(days):
                        # Load existing text or empty
                        val = plan[d][row] if row < len(plan[d]) else ""
                        inp = row_cols[idx+1].text_input(f"{d}_{row}", value=val, key=f"ip_{d}_{row}", label_visibility="collapsed")
                        row_data[d] = inp
                    
                    row_inputs.append(row_data)
                
                # Lunch/Noon row (Row 6)
                st.markdown("---")
                noon_cols = st.columns(6)
                noon_cols[0].markdown("**NOON**")
                for i in range(5):
                    noon_cols[i+1].markdown("**LUNCH**")
                st.markdown("---")
                
                # Last 2 rows (Row 7 & 8)
                for row in range(5, 7):
                    row_cols = st.columns(6)
                    time_val = row_cols[0].text_input(f"time_{row}", value="13:00 - 14:00", key=f"t_{row}", label_visibility="collapsed")
                    
                    row_data = {"time": time_val}
                    for idx, d in enumerate(days):
                        val = plan[d][row] if row < len(plan[d]) else ""
                        inp = row_cols[idx+1].text_input(f"{d}_{row}", value=val, key=f"ip_{d}_{row}", label_visibility="collapsed")
                        row_data[d] = inp
                    row_inputs.append(row_data)

                submitted = st.form_submit_button("💾 Save Study Plan")
                
                if submitted:
                    # Save data back to dict
                    new_plan = {d: [] for d in days}
                    for row_data in row_inputs:
                        for d in days:
                            new_plan[d].append(row_data[d])
                    
                    data[plan_roll]['study_plan'] = new_plan
                    save_data(data)
                    st.markdown("<div class='alert-box'>✅ Study Plan updated successfully!</div>", unsafe_allow_html=True)
                    st.rerun()

        elif plan_roll:
            st.markdown("<div class='alert-box error'>❌ Roll number not found. Please verify and try again.</div>", unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
