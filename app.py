import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime
import io
# Import ReportLab for highly customized PDF generation
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch

# ---------- CONFIGURATION & DATA CONSTANTS ----------
FILE_NAME = "students.json"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "1234"
# The subjects utilized by this application
SUBJECTS = ["English", "Urdu", "Math", "Science", "Sindhi", "Islamiyat", "Social Studies"]
TOTAL_MARKS = 700

# ---------- PREMIUM UI CONFIGURATION (CSS INJECTION) ----------
st.set_page_config(page_title="Anderson Family Homeschool Portal", page_icon="📘", layout="wide")

# Custom CSS to override Streamlit defaults and inject Glassmorphism, Neomorphism, and Premium Typography
st.markdown("""
<style>
    /* Import premium Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&family=Poppins:wght@400;600;700&display=swap');
    
    /* Global App Styling - Dark Mode Premium Background */
    .stApp {
        background: linear-gradient(145deg, #1e1e1e 0%, #2a2a2a 100%);
        color: #f5f0e6; /* Beige-cream for readability */
        font-family: 'Inter', sans-serif;
    }

    /* Glassmorphism Sidebar */
    [data-testid="stSidebar"] {
        background: rgba(122, 76, 52, 0.15) !important;
        backdrop-filter: blur(16px) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08);
        box-shadow: 4px 0 25px rgba(0,0,0,0.3);
    }
    [data-testid="stSidebar"] * {
        color: #f5f0e6 !important;
    }

    /* Premium Cards / Containers */
    .premium-glass-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 25px;
        margin-bottom: 20px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
        transition: transform 0.2s ease;
    }

    /* Custom Inputs (Redefining Streamlit widgets) */
    div[data-testid="stTextInput"] label {
        color: #c83c2f !important; /* Burnt Orange/Red */
        font-weight: 600;
        font-family: 'Poppins', sans-serif;
    }
    div[data-testid="stTextInput"] input {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 10px !important;
        color: white !important;
        backdrop-filter: blur(5px) !important;
        font-family: 'Inter', sans-serif;
    }
    div[data-testid="stTextInput"] input:focus {
        border-color: #c83c2f !important;
        box-shadow: 0 0 15px rgba(200, 60, 47, 0.3) !important;
    }

    /* Premium Button Styling (Hover effects, gradients) */
    div.stButton > button {
        background: linear-gradient(135deg, #7a4c34 0%, #a66a40 100%) !important;
        color: white !important;
        border-radius: 30px !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        padding: 10px 24px !important;
        font-weight: 600 !important;
        font-family: 'Poppins', sans-serif !important;
        letter-spacing: 1px !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 15px rgba(122, 76, 52, 0.5) !important;
        width: 100%;
    }
    div.stButton > button:hover {
        transform: translateY(-3px) scale(1.02) !important;
        box-shadow: 0 8px 25px rgba(122, 76, 52, 0.8) !important;
        border-color: #ffffff !important;
    }

    /* Admin Dataframe Styling (Neomorphism Table) */
    .stDataFrame {
        background: transparent !important;
    }
    .stDataFrame table {
        border-radius: 12px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        background: rgba(255, 255, 255, 0.03) !important;
    }
    .stDataFrame th {
        background: #7a4c34 !important;
        color: #ffffff !important;
        font-family: 'Poppins', sans-serif !important;
    }
    .stDataFrame td {
        color: #e0d7c8 !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05) !important;
    }

    /* Custom Alerts Implementation */
    .premium-alert-success {
        background: rgba(46, 204, 113, 0.15);
        border-left: 6px solid #2ecc71;
        padding: 15px;
        border-radius: 10px;
        backdrop-filter: blur(5px);
        color: #d1f2eb;
        font-family: 'Inter', sans-serif;
        margin-bottom: 15px;
    }
    .premium-alert-error {
        background: rgba(231, 76, 60, 0.15);
        border-left: 6px solid #e74c3c;
        padding: 15px;
        border-radius: 10px;
        backdrop-filter: blur(5px);
        color: #fadbd8;
        font-family: 'Inter', sans-serif;
        margin-bottom: 15px;
    }
    .premium-alert-info {
        background: rgba(52, 152, 219, 0.15);
        border-left: 6px solid #3498db;
        padding: 15px;
        border-radius: 10px;
        backdrop-filter: blur(5px);
        color: #d6eaf8;
        font-family: 'Inter', sans-serif;
    }
</style>
""", unsafe_allow_html=True)

# ---------- HELPER FUNCTIONS ----------
def load_data():
    if os.path.exists(FILE_NAME):
        try:
            with open(FILE_NAME, "r") as file:
                return json.load(file)
        except (json.JSONDecodeError, IOError):
            return {}
    return {}

def save_data(data):
    with open(FILE_NAME, "w") as file:
        json.dump(data, file, indent=4)

def get_grade_gpa(percentage):
    """Calculates letter grade, GPA, and percentage range based on the provided image's Grading Key."""
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

def get_teacher_remarks(percentage):
    """Generates remarks for the PDF."""
    if percentage >= 90: return "Excellent"
    elif percentage >= 80: return "Good"
    elif percentage >= 70: return "Satisfactory"
    elif percentage >= 60: return "Needs Improvement"
    else: return "Requires Attention"

# ---------- PREMIUM PDF GENERATION (REPORTLAB) ----------
def generate_pdf_report(roll_number, student_name, student_class, marks_dict, date_today):
    """
    Generates a byte-stream PDF mirroring the provided Canva template exactly.
    Returns a BytesIO object ready for download.
    """
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # COLORS (Derived from the provided Canva image)
    brown_dark = colors.HexColor('#604227')
    brown_brand = colors.HexColor('#7a4c34')
    red_brand = colors.HexColor('#c83c2f')
    cream_bg = colors.HexColor('#f5f0e6')
    cream_light = colors.HexColor('#eae2d7')
    
    # 1. BACKGROUND & DECORATIVE CIRCLES (Canva-style aesthetic)
    c.setFillColor(cream_bg)
    c.rect(0, 0, width, height, fill=1, stroke=0)
    
    # Draw background decorative overlapping circles
    c.setFillColor(colors.HexColor('#e0d7c8'))
    c.circle(70, height - 60, 50, stroke=0, fill=1)
    c.setFillColor(colors.HexColor('#d4c8b6'))
    c.circle(width - 70, height - 150, 80, stroke=0, fill=1)
    c.setFillColor(colors.HexColor('#c83c2f')) # Red semi-transparent overlay
    c.setFillAlpha(0.1)
    c.circle(145, height - 80, 45, stroke=0, fill=1)
    c.setFillAlpha(1)

    # 2. HEADER BOX (Banner)
    header_x = (width - 250) / 2
    header_y = height - 90
    c.setFillColor(brown_brand)
    c.roundRect(header_x, header_y, 250, 55, 10, fill=1, stroke=0)
    
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(width/2, height - 65, "Progress Report")
    c.setFillColor(brown_brand)
    c.setFont("Helvetica", 12)
    c.drawCentredString(width/2, height - 120, "Anderson Family Homeschool")

    # 3. STUDENT INFO FORM SECTION
    c.setStrokeColor(brown_brand)
    c.setLineWidth(1.5)
    x_margin = 50
    
    # Labels (Red)
    c.setFillColor(red_brand)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(x_margin, height - 160, "Student Name:")
    c.drawString(x_margin, height - 195, "Grade:")
    c.drawString(x_margin + 300, height - 160, "School Year:")
    c.drawString(x_margin + 300, height - 195, "Teacher:")
    
    # Underlines (In case fields are empty)
    c.setStrokeColor(colors.grey)
    c.setLineWidth(0.8)
    c.line(x_margin, height - 170, x_margin + 250, height - 170)
    c.line(x_margin, height - 205, x_margin + 250, height - 205)
    c.line(x_margin + 300, height - 170, x_margin + 520, height - 170)
    c.line(x_margin + 300, height - 205, x_margin + 520, height - 205)
    
    # Fill Student Info (Black/White text)
    c.setFillColor(brown_dark)
    c.setFont("Helvetica", 12)
    c.drawString(x_margin + 5, height - 175, student_name)
    c.drawString(x_margin + 5, height - 210, student_class)
    c.drawString(x_margin + 305, height - 175, date_today)
    c.drawString(x_margin + 305, height - 210, "Faculty (Auto-Generated)")

    # 4. TABLE CONSTRUCTION
    table_x = x_margin
    table_y = height - 240
    table_w = 495
    col_widths = [230, 75, 75, 115] # Course Title, Units, Grade, Remarks
    row_h = 22
    
    # Table Header Background (Brown)
    c.setFillColor(brown_brand)
    c.rect(table_x, table_y, table_w, 30, fill=1, stroke=0)
    c.setStrokeColor(colors.white)
    c.setLineWidth(0.5)
    
    # Table Header Text (White)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(table_x + 10, table_y + 10, "Course Title")
    c.drawString(table_x + 235, table_y + 10, "No. of Units")
    c.drawString(table_x + 315, table_y + 10, "Course Grade")
    c.drawString(table_x + 385, table_y + 10, "Teacher's Remarks")
    
    # Draw Table Rows
    current_y = table_y - row_h
    units = "1"
    
    for subject in SUBJECTS:
        # Border Lines (Optional clean grid)
        c.setStrokeColor(colors.HexColor('#d0c8bc'))
        c.setLineWidth(0.5)
        
        # Fetch Subject Data
        mark = marks_dict.get(subject, 0)
        perc_sub = (mark / 100) * 100 if mark else 0 # Assuming max marks per subject is 100
        grade, _, _ = get_grade_gpa(perc_sub)
        remark = get_teacher_remarks(perc_sub)
        
        # Draw Row Background with slight transparency (Glass/Beige effect)
        if current_y % 2 == 0: # Alternate faint row colors if desired, but image looks transparent/beige
             c.setFillColor(colors.white)
             c.setFillAlpha(0.1)
             c.rect(table_x, current_y, table_w, row_h, fill=1, stroke=0)
             c.setFillAlpha(1)
        
        # Draw Col 1 (Course Title - Red)
        c.setFillColor(red_brand)
        c.setFont("Helvetica", 10)
        c.drawString(table_x + 10, current_y + 6, subject)
        
        # Draw Col 2 (Units - Black)
        c.setFillColor(brown_dark)
        c.drawString(table_x + 260, current_y + 6, units)
        
        # Draw Col 3 (Course Grade - Black)
        c.drawString(table_x + 335, current_y + 6, grade)
        
        # Draw Col 4 (Remarks - Black)
        c.drawString(table_x + 400, current_y + 6, remark)
        
        current_y -= row_h
    
    # 5. GRADING KEY SECTION (Matching Canva template structure)
    key_x = x_margin
    key_y = current_y - 30
    key_h = 110
    
    # Grading Key Label (Brown Box)
    c.setFillColor(brown_brand)
    c.rect(key_x, key_y, 130, key_h, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(key_x + 65, key_y + 55, "GRADING")
    c.drawCentredString(key_x + 65, key_y + 40, "KEY")
    
    # Grading Key Data (Beige Background Box)
    c.setFillColor(cream_light)
    c.setFillAlpha(0.8)
    c.rect(key_x + 130, key_y, 365, key_h, fill=1, stroke=0)
    c.setFillAlpha(1)
    c.setFillColor(brown_dark)
    c.setFont("Helvetica", 9)
    
    # Text Content for Grading Key (Left Column)
    g_y = key_y + 90
    c.drawString(key_x + 140, g_y, "A = 93% to 100% | 4.0/4.0")
    c.drawString(key_x + 140, g_y - 12, "A- = 90% to 92% | 3.7/4.0")
    c.drawString(key_x + 140, g_y - 24, "B+ = 87% to 89% | 3.3/4.0")
    c.drawString(key_x + 140, g_y - 36, "B = 83% to 86% | 3.0/4.0")
    c.drawString(key_x + 140, g_y - 48, "B- = 80% to 82% | 2.7/4.0")
    c.drawString(key_x + 140, g_y - 60, "C+ = 77% to 79% | 2.3/4.0")
    
    # Text Content for Grading Key (Right Column)
    c.drawString(key_x + 280, g_y, "C = 73% to 76% | 2.0/4.0")
    c.drawString(key_x + 280, g_y - 12, "C- = 70% to 72% | 1.7/4.0")
    c.drawString(key_x + 280, g_y - 24, "D+ = 67% to 69% | 1.3/4.0")
    c.drawString(key_x + 280, g_y - 36, "D = 63% to 66% | 1.0/4.0")
    c.drawString(key_x + 280, g_y - 48, "D- = 60% to 62% | 0.7/4.0")
    c.drawString(key_x + 280, g_y - 60, "F = 0% to 59% | 0.0/4.0")
    c.drawString(key_x + 280, g_y - 72, "I = Incomplete")

    # 6. FOOTER SECTION
    footer_y = 0
    footer_h = 40
    c.setFillColor(brown_brand)
    c.rect(0, footer_y, width, footer_h, fill=1, stroke=0)
    
    # Quarter Boxes
    box_w = 110
    box_h = 25
    box_y = 8
    quarters = ["Quarter One", "Quarter Two", "Quarter Three", "Quarter Four"]
    
    for i, q in enumerate(quarters):
        box_x = 40 + (i * 130)
        c.setFillColor(colors.white)
        c.rect(box_x, box_y, box_w, box_h, fill=1, stroke=0)
        c.setFillColor(brown_brand)
        c.setFont("Helvetica", 9)
        c.drawCentredString(box_x + (box_w/2), box_y + 13, q)

    # Finalize PDF
    c.save()
    buffer.seek(0)
    return buffer

# ---------- DATA PREPARATION ----------
data = load_data()

# ---------- APP NAVIGATION ----------
st.sidebar.markdown(
    "<h2 style='text-align:center; color:#c83c2f; font-family:Poppins, sans-serif;'>📘 ELITE PORTAL</h2>", 
    unsafe_allow_html=True
)
st.sidebar.markdown("<hr style='border-top: 1px solid rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
choice = st.sidebar.radio("NAVIGATION", ["🏠 MAIN MENU", "🔐 ADMIN ACCESS", "👨‍🎓 STUDENT RESULT"], index=0)

# ---------- PAGE 1: MAIN MENU ----------
if choice == "🏠 MAIN MENU":
    st.markdown(
        "<h1 style='font-family: Poppins, sans-serif; text-align:center;'>Anderson Family <br><span style='color:#c83c2f;'>Homeschool Management</span></h1>", 
        unsafe_allow_html=True
    )
    st.markdown(
        """
        <div class='premium-glass-card' style='text-align:center;'>
            <h3>Enter the secure portal below.</h3>
            <p>Access real-time analytics, encrypted student records, and dynamic report generation.</p>
            <p style='color:#c83c2f; font-size: 12px;'>* System designed to generate Canva-standard PDF report cards.</p>
        </div>
        """, 
        unsafe_allow_html=True
    )
    st.image("https://img.freepik.com/free-vector/gradient-education-elements-background_23-2148851503.jpg", use_container_width=True)

# ---------- PAGE 2: ADMIN ACCESS ----------
elif choice == "🔐 ADMIN ACCESS":
    st.markdown("<h2 style='font-family: Poppins, sans-serif;'>🛡️ Secure Admin Terminal</h2>", unsafe_allow_html=True)
    
    if 'admin_auth' not in st.session_state: 
        st.session_state.admin_auth = False

    if not st.session_state.admin_auth:
        with st.form("Login"):
            st.markdown("<div class='premium-glass-card'><h4>Authentication</h4>", unsafe_allow_html=True)
            u = st.text_input("Username", placeholder="admin")
            p = st.text_input("Password", type="password")
            submitted = st.form_submit_button("UNSEAL ACCESS")
            st.markdown("</div>", unsafe_allow_html=True)
            
            if submitted:
                if u == ADMIN_USERNAME and p == ADMIN_PASSWORD:
                    st.session_state.admin_auth = True
                    st.rerun()
                else:
                    st.markdown("<div class='premium-alert-error'>Access Denied: Invalid Credentials.</div>", unsafe_allow_html=True)
    else:
        st.sidebar.button("🛑 LOGOUT", on_click=lambda: st.session_state.update({"admin_auth": False}))
        
        tab1, tab2, tab3, tab4 = st.tabs(["📝 Register New", "🗄️ View Database", "🔄 Update Marks", "📥 Export Data"])

        with tab1:
            st.markdown("<div class='premium-glass-card'>", unsafe_allow_html=True)
            st.subheader("Register New Student Record")
            with st.form("add_form", clear_on_submit=True):
                col1, col2 = st.columns(2)
                r = col1.text_input("Roll Number")
                n = col2.text_input("Student Name")
                cl = st.text_input("Class")
                st.write("Subject Marks (Max 100)")
                marks = {}
                m_cols = st.columns(2)
                for i, sub in enumerate(SUBJECTS):
                    marks[sub] = m_cols[i%2].number_input(sub, 0, 100)
                
                submitted_form = st.form_submit_button("SUBMIT DATA")
                if submitted_form:
                    if r and n:
                        data[r] = {
                            "name": n, 
                            "class": cl, 
                            "marks": marks, 
                            "date": str(datetime.now().date())
                        }
                        save_data(data)
                        st.markdown("<div class='premium-alert-success'>Record for {} encrypted & saved successfully!</div>".format(n), unsafe_allow_html=True)
                    else:
                        st.markdown("<div class='premium-alert-error'>Critical fields (Roll / Name) missing!</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with tab2:
            st.subheader("Global Student Database")
            if data:
                db_list = [{"Roll": r, "Name": i['name'], "Class": i['class'], "Total": sum(i['marks'].values())} for r, i in data.items()]
                st.dataframe(pd.DataFrame(db_list), use_container_width=True)
            else:
                st.markdown("<div class='premium-alert-info'>No records found in the encrypted vault.</div>", unsafe_allow_html=True)

        with tab3:
            st.subheader("Modification Interface")
            u_roll = st.text_input("Target Roll Number")
            if u_roll in data:
                with st.form("upd"):
                    st.info(f"Modifying Record for: {data[u_roll]['name']}")
                    new_m = {sub: st.number_input(sub, 0, 100, value=data[u_roll]['marks'].get(sub, 0)) for sub in SUBJECTS}
                    if st.form_submit_button("OVERWRITE MARKS"):
                        data[u_roll]['marks'] = new_m
                        save_data(data)
                        st.markdown("<div class='premium-alert-success'>Buffer overwritten successfully!</div>", unsafe_allow_html=True)
            elif u_roll:
                st.markdown("<div class='premium-alert-error'>Target Roll Number not found.</div>", unsafe_allow_html=True)

        with tab4:
            st.subheader("Data Extraction")
            if data:
                export_list = []
                for r, info in data.items():
                    row = {"Roll": r, "Name": info['name'], "Class": info['class']}
                    row.update(info['marks'])
                    t = sum(info['marks'].values())
                    p = (t/700)*100
                    grade, gpa, _ = get_grade_gpa(p)
                    row.update({"Total": t, "Percentage": f"{p:.2f}%", "Grade": grade})
                    export_list.append(row)
                
                csv_data = pd.DataFrame(export_list).to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📤 GENERATE & DOWNLOAD CSV", 
                    data=csv_data, 
                    file_name="Elite_Student_Data.csv",
                    mime="text/csv"
                )
            else:
                st.markdown("<div class='premium-alert-info'>No data available for extraction.</div>", unsafe_allow_html=True)

# ---------- PAGE 3: STUDENT RESULT ----------
elif choice == "👨‍🎓 STUDENT RESULT":
    st.markdown("<h2 style='font-family: Poppins, sans-serif;'>🎓 Digital Marksheet Portal</h2>", unsafe_allow_html=True)
    
    st.markdown("<div class='premium-glass-card'>", unsafe_allow_html=True)
    st.markdown("<h4>Verify Identity</h4>", unsafe_allow_html=True)
    roll = st.text_input("Enter Encrypted Roll Number", placeholder="e.g. 1001")
    
    if st.button("🔍 RETRIEVE RESULT"):
        if roll in data:
            s = data[roll]
            st.balloons()
            
            # Display in custom Premium Glass Card
            total = sum(s['marks'].values())
            perc = (total/TOTAL_MARKS)*100
            grade, gpa, _ = get_grade_gpa(perc)
            
            st.markdown(
                f"""
                <div class='premium-glass-card' style='border-top: 4px solid #c83c2f;'>
                    <h2 style='margin:0; color:#ffffff; font-family: Poppins, sans-serif;'>{s['name']}</h2>
                    <p style='color:#c83c2f;'>Roll: {roll} | Class: {s['class']} | Session: 2024-25</p>
                    <hr style='border: 0; height: 1px; background: linear-gradient(to right, transparent, rgba(255,255,255,0.1), transparent);'>
                    
                    <div style='display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 15px;'>
                        <div style='background: rgba(255,255,255,0.05); padding: 15px; border-radius: 12px;'>
                            <p style='margin:0; font-size: 12px; color: #a0a0a0;'>TOTAL OBTAINED</p>
                            <p style='margin:0; font-size: 24px; font-weight: bold; color: #ffffff;'>{total} / {TOTAL_MARKS}</p>
                        </div>
                        <div style='background: rgba(255,255,255,0.05); padding: 15px; border-radius: 12px;'>
                            <p style='margin:0; font-size: 12px; color: #a0a0a0;'>PERCENTAGE</p>
                            <p style='margin:0; font-size: 24px; font-weight: bold; color: #ffffff;'>{perc:.2f}%</p>
                        </div>
                    </div>
                    
                    <div style='margin-top: 15px; display: flex; justify-content: space-between; align-items: center;'>
                        <p style='margin:0; color: #ffffff;'>Letter Grade:</p>
                        <p style='margin:0; font-size: 28px; font-weight: 800; color: #c83c2f; font-family: Poppins, sans-serif;'>{grade}</p>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            # Subject breakdown table using Pandas and Streamlit dataframe (styled by our global CSS)
            df_m = pd.DataFrame(list(s['marks'].items()), columns=["Subject", "Obtained"])
            st.markdown("<p style='color:#c83c2f; font-weight:bold;'>Detailed Subject Breakdown:</p>", unsafe_allow_html=True)
            st.dataframe(df_m, use_container_width=True)

            # PDF GENERATION AND DOWNLOAD BUTTON
            today_str = datetime.now().strftime("%Y-%m-%d")
            pdf_buffer = generate_pdf_report(roll, s['name'], s['class'], s['marks'], today_str)
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.download_button(
                label="📥 Download Official Progress Report (PDF)",
                data=pdf_buffer,
                file_name=f"{s['name']}_{roll}_Progress_Report.pdf",
                mime="application/pdf",
                key="pdf_download"
            )

        else:
            st.markdown("<div class='premium-alert-error'>⛔ ERROR: Roll Number not verified in system.</div>", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
