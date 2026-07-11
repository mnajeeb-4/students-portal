import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime
import io
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
import plotly.graph_objects as go

# ---------- CONFIGURATION & DATA CONSTANTS ----------
FILE_NAME = "students.json"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "1234"
SUBJECTS = ["English", "Urdu", "Math", "Science", "Sindhi", "Islamiyat", "Social Studies"]
TOTAL_MARKS = 700

# ---------- PREMIUM UI CONFIGURATION (CSS INJECTION) ----------
st.set_page_config(page_title="Elite Academy", page_icon="🏆", layout="wide")

# Initialize theme state
if 'dark_theme' not in st.session_state:
    st.session_state.dark_theme = True

# Dynamic CSS based on Theme Toggle
theme_bg = "linear-gradient(135deg, #0f0c29, #302b63, #24243e)" if st.session_state.dark_theme else "linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)"
text_color = "#ffffff" if st.session_state.dark_theme else "#1a1a1a"
input_bg = "rgba(255, 255, 255, 0.15)" if st.session_state.dark_theme else "rgba(0, 0, 0, 0.05)"
input_border = "rgba(255, 255, 255, 0.3)" if st.session_state.dark_theme else "rgba(0, 0, 0, 0.1)"
card_bg = "rgba(255, 255, 255, 0.08)" if st.session_state.dark_theme else "rgba(255, 255, 255, 0.6)"
shadow_color = "rgba(0, 0, 0, 0.5)" if st.session_state.dark_theme else "rgba(0, 0, 0, 0.1)"

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&family=Poppins:wght@400;600;700&display=swap');
    
    .stApp {{
        background: {theme_bg};
        color: {text_color};
        font-family: 'Inter', sans-serif;
        background-size: 400% 400%;
        animation: gradientShift 15s ease infinite;
    }}
    
    @keyframes gradientShift {{
        0% {{ background-position: 0% 50%; }}
        50% {{ background-position: 100% 50%; }}
        100% {{ background-position: 0% 50%; }}
    }}

    [data-testid="stSidebar"] {{
        background: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(20px) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }}
    
    /* Fix: Text Input White on White Bug FIXED HERE */
    div[data-testid="stTextInput"] input, div[data-testid="stNumberInput"] input {{
        background: {input_bg} !important;
        border: 1px solid {input_border} !important;
        color: {text_color} !important; /* Colors fixed so text is visible */
        border-radius: 12px !important;
        padding: 10px 15px !important;
        backdrop-filter: blur(5px);
        transition: 0.3s ease;
    }}
    div[data-testid="stTextInput"] input:focus, div[data-testid="stNumberInput"] input:focus {{
        border-color: #c83c2f !important;
        box-shadow: 0 0 20px rgba(200, 60, 47, 0.3);
    }}
    
    /* Premium Cards */
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
    .premium-glass-card:hover {{
        transform: translateY(-5px);
        box-shadow: 0 20px 60px {shadow_color};
    }}

    /* Premium Buttons */
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
    div.stButton > button:hover {{
        transform: scale(1.05) !important;
        box-shadow: 0 8px 30px rgba(200, 60, 47, 0.7) !important;
    }}

    /* Custom Metrics */
    .metric-card {{
        background: rgba(255,255,255,0.05);
        border-radius: 16px;
        padding: 20px;
        text-align: center;
        border: 1px solid rgba(255,255,255,0.1);
    }}
    .metric-card h3 {{ margin:0; color:#c83c2f; font-size:12px; letter-spacing:2px; text-transform:uppercase; }}
    .metric-card h2 {{ margin:0; font-size:38px; font-weight:700; }}

    /* Modern Alerts */
    .alert-box {{
        padding: 15px;
        border-radius: 12px;
        border-left: 6px solid #2ecc71;
        background: rgba(46, 204, 113, 0.1);
        margin-bottom: 10px;
    }}
    .alert-box.error {{ border-left-color: #e74c3c; background: rgba(231, 76, 60, 0.1); }}
</style>
""", unsafe_allow_html=True)

# ---------- HELPERS ----------
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

def get_grade_gpa(percentage):
    if percentage >= 93: return "A", "4.0", "93-100%"
    elif percentage >= 90: return "A-", "3.7", "90-92%"
    elif percentage >= 87: return "B+", "3.3", "87-89%"
    elif percentage >= 83: return "B", "3.0", "83-86%"
    elif percentage >= 80: return "B-", "2.7", "80-82%"
    elif percentage >= 77: return "C+", "2.3", "77-79%"
    elif percentage >= 73: return "C", "2.0", "73-76%"
    elif percentage >= 70: return "C-", "1.7", "70-72%"
    elif percentage >= 67: return "D+", "1.3", "67-69%"
    elif percentage >= 63: return "D", "1.0", "63-66%"
    elif percentage >= 60: return "D-", "0.7", "60-62%"
    else: return "F", "0.0", "0-59%"

# ---------- PDF (UPGRADED) ----------
def generate_pdf_report(roll, name, cls, marks_dict, date_today):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    c.setFillColor(colors.HexColor('#f5f0e6'))
    c.rect(0, 0, width, height, fill=1, stroke=0)
    c.setFillColor(colors.HexColor('#604227'))
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(width/2, height-70, "PROGRESS REPORT")
    c.setFont("Helvetica", 12)
    c.drawCentredString(width/2, height-95, "Anderson Family Homeschool")
    
    # Student Info
    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(colors.HexColor('#c83c2f'))
    c.drawString(50, height-140, "Student Name:")
    c.drawString(50, height-165, "Grade:")
    c.drawString(300, height-140, "Date:")
    c.drawString(300, height-165, "Roll No:")
    
    c.setFillColor(colors.black)
    c.setFont("Helvetica", 11)
    c.drawString(130, height-140, name)
    c.drawString(100, height-165, cls)
    c.drawString(340, height-140, date_today)
    c.drawString(360, height-165, roll)
    
    # Table
    y = height-200
    c.setFillColor(colors.HexColor('#7a4c34'))
    c.rect(50, y, 500, 25, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(55, y+8, "SUBJECT")
    c.drawString(230, y+8, "MARKS")
    c.drawString(350, y+8, "GRADE")
    c.drawString(450, y+8, "REMARKS")
    
    y -= 25
    for sub in SUBJECTS:
        mark = marks_dict.get(sub, 0)
        perc = (mark/100)*100
        grade, _, _ = get_grade_gpa(perc)
        remark = "Excellent" if perc>=90 else "Good" if perc>=80 else "Satisfactory" if perc>=70 else "Needs Improvement"
        
        c.setFillColor(colors.black)
        c.setFont("Helvetica", 10)
        c.drawString(55, y+8, sub)
        c.drawString(230, y+8, str(mark))
        c.drawString(350, y+8, grade)
        c.drawString(450, y+8, remark)
        y -= 20
    
    # Footer
    c.setFillColor(colors.HexColor('#7a4c34'))
    c.rect(0, 0, width, 40, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("Helvetica", 8)
    c.drawString(20, 15, "Generated by Elite Student Portal v2.0")
    
    c.save()
    buffer.seek(0)
    return buffer

# ---------- DATA ----------
data = load_data()
if 'admin_auth' not in st.session_state: st.session_state.admin_auth = False

# ---------- SIDEBAR ----------
with st.sidebar:
    st.markdown("<h3 style='text-align:center; color:#c83c2f;'>🏆 ELITE</h3>", unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)
    # Theme Toggle (Million-dollar feature)
    st.session_state.dark_theme = st.toggle("🌙 Dark Mode", value=st.session_state.dark_theme)
    choice = st.radio("Navigation", ["🏠 Home", "🛡️ Admin Panel", "📋 Student Result"])

# ---------- PAGE 1: HOME ----------
if choice == "🏠 Home":
    st.markdown("<h1 style='font-family:Poppins;'>The Future of <span style='color:#c83c2f;'>Education Management</span></h1>", unsafe_allow_html=True)
    st.markdown("<p style='opacity:0.8;'>Track, Analyze, and Generate Million-Dollar Reports in seconds.</p>", unsafe_allow_html=True)
    st.markdown("<div class='premium-glass-card'><h4>🚀 Quick Start</h4>Select 'Admin Panel' to add students, or 'Student Result' to view reports.</div>", unsafe_allow_html=True)

# ---------- PAGE 2: ADMIN ----------
elif choice == "🛡️ Admin Panel":
    if not st.session_state.admin_auth:
        with st.form("admin_login"):
            st.markdown("<div class='premium-glass-card'>", unsafe_allow_html=True)
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.form_submit_button("Unseal"):
                if u == ADMIN_USERNAME and p == ADMIN_PASSWORD:
                    st.session_state.admin_auth = True
                    st.rerun()
                else: st.markdown("<div class='alert-box error'>🔒 Invalid Credentials</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.sidebar.button("🚪 Logout", on_click=lambda: st.session_state.update({"admin_auth": False}))
        
        # DASHBOARD STATS (Million-dollar feature)
        st.subheader("📊 Executive Dashboard")
        if data:
            totals = [sum(i['marks'].values()) for i in data.values()]
            c1, c2, c3 = st.columns(3)
            c1.markdown(f"<div class='metric-card'><h3>Total Students</h3><h2>{len(data)}</h2></div>", unsafe_allow_html=True)
            c2.markdown(f"<div class='metric-card'><h3>Avg Performance</h3><h2>{sum(totals)/len(totals)/7:.1f}%</h2></div>", unsafe_allow_html=True)
            top_student = max(data.items(), key=lambda x: sum(x[1]['marks'].values()))
            c3.markdown(f"<div class='metric-card'><h3>🏆 Top Scorer</h3><h2>{top_student[1]['name']}</h2></div>", unsafe_allow_html=True)
        
        tab1, tab2, tab3 = st.tabs(["📝 Add Student", "📂 Database (Searchable)", "📥 Export"])
        
        with tab1:
            with st.form("add_student"):
                r = st.text_input("Roll Number")
                n = st.text_input("Student Name")
                cl = st.text_input("Class")
                marks = {}
                cols = st.columns(3)
                for i, sub in enumerate(SUBJECTS):
                    marks[sub] = cols[i%3].number_input(sub, 0, 100, 0)
                
                if st.form_submit_button("Add Record"):
                    if r and n:
                        data[r] = {"name": n, "class": cl, "marks": marks, "date": str(datetime.now().date())}
                        save_data(data)
                        st.markdown("<div class='alert-box'>✅ Record Saved successfully!</div>", unsafe_allow_html=True)
                    else:
                        st.markdown("<div class='alert-box error'>❌ Roll and Name are mandatory</div>", unsafe_allow_html=True)
        
        with tab2:
            search_query = st.text_input("🔍 Search by Roll or Name")
            if data:
                df_data = []
                for r, info in data.items():
                    if search_query.lower() in r.lower() or search_query.lower() in info['name'].lower():
                        t = sum(info['marks'].values())
                        p = (t/TOTAL_MARKS)*100
                        g, _, _ = get_grade_gpa(p)
                        df_data.append({"Roll": r, "Name": info['name'], "Total": t, "Grade": g})
                if df_data:
                    st.dataframe(pd.DataFrame(df_data), use_container_width=True)
                else:
                    st.info("No matching records found.")
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

# ---------- PAGE 3: STUDENT ----------
elif choice == "📋 Student Result":
    st.subheader("📋 Student Result Portal")
    with st.container():
        st.markdown("<div class='premium-glass-card'>", unsafe_allow_html=True)
        roll = st.text_input("Enter your Roll Number")
        if st.button("🔍 Generate Report"):
            if roll in data:
                s = data[roll]
                total = sum(s['marks'].values())
                perc = (total/TOTAL_MARKS)*100
                grade, gpa, _ = get_grade_gpa(perc)
                
                # Display Header
                st.markdown(f"""
                <div style='display:flex; justify-content:space-between;'>
                    <div><h2 style='margin:0;'>{s['name']}</h2>
                    <p style='color:#c83c2f;'>Roll: {roll} | Class: {s['class']}</p></div>
                    <div><p style='font-size:32px; margin:0; color:#c83c2f;'>{grade}</p></div>
                </div>
                <hr style='border:0; height:1px; background:linear-gradient(90deg, transparent, #c83c2f, transparent);'>
                """, unsafe_allow_html=True)
                
                # Subject Data Display
                df = pd.DataFrame(list(s['marks'].items()), columns=["Subject", "Marks"])
                df["Percentage"] = (df["Marks"]/100*100).round(1)
                df["Grade"] = df["Percentage"].apply(lambda x: get_grade_gpa(x)[0])
                
                c1, c2 = st.columns([3, 2])
                with c1:
                    st.dataframe(df, use_container_width=True)
                    st.metric("Grand Total", f"{total} / {TOTAL_MARKS}")
                    st.metric("GPA (4.0 Scale)", gpa)
                
                with c2:
                    # Radar Chart (Plotly - Million dollar feature)
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
                            font=dict(color='white')
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    except Exception as e:
                        st.write("Plotly Radar Chart Unavailable.")

                # PDF Download
                pdf = generate_pdf_report(roll, s['name'], s['class'], s['marks'], str(datetime.now().date()))
                st.download_button("📥 Download Official PDF", data=pdf, file_name=f"{s['name']}_Report.pdf")
                
            else:
                st.markdown("<div class='alert-box error'>❌ Roll number not found in system.</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
