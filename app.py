import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime

# ---------- PRE-REQUISITES ----------
FILE_NAME = "students.json"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "1234"
SUBJECTS = ["English", "Urdu", "Math", "Science", "Sindhi", "Islamiyat", "Social Studies"]
TOTAL_MARKS = 700

# ---------- PREMIUM UI CONFIG ----------
st.set_page_config(page_title="Elite Student Portal", page_icon="💎", layout="wide")

# Custom CSS for Premium Look
st.markdown("""
    <style>
    /* Background Gradient */
    .stApp {
        background: linear-gradient(135deg, #1a2a6c 0%, #b21f1f 50%, #fdbb2d 100%);
        color: white;
    }
    
    /* Glassmorphism Sidebar */
    [data-testid="stSidebar"] {
        background-color: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(15px);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Premium Cards */
    .premium-card {
        background: rgba(255, 255, 255, 0.1);
        padding: 25px;
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(10px);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        margin-bottom: 20px;
    }

    /* Animated Buttons */
    .stButton>button {
        background: linear-gradient(45deg, #00d2ff, #3a7bd5);
        color: white;
        border-radius: 30px;
        border: none;
        padding: 10px 25px;
        transition: 0.4s ease;
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .stButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0 5px 15px rgba(0, 210, 255, 0.4);
    }

    /* Metric Styling */
    [data-testid="stMetricValue"] {
        color: #00d2ff !important;
    }
    </style>
    """, unsafe_allow_html=True)

# ---------- LOGIC FUNCTIONS ----------
def load_data():
    if os.path.exists(FILE_NAME):
        try:
            with open(FILE_NAME, "r") as file: return json.load(file)
        except: return {}
    return {}

def save_data(data):
    with open(FILE_NAME, "w") as file:
        json.dump(data, file, indent=4)

def get_grade_styles(percentage):
    if percentage >= 80: return "🌟 A-1", "#00FF88"
    elif percentage >= 70: return "✨ A", "#00D2FF"
    elif percentage >= 60: return "✅ B", "#FFD700"
    elif percentage >= 50: return "🆗 C", "#FFA500"
    else: return "❌ Fail", "#FF4B4B"

# ---------- DATA LOADING ----------
data = load_data()

# ---------- NAVIGATION ----------
st.sidebar.markdown("<h1 style='text-align: center; color: white;'>💎 ELITE SMS</h1>", unsafe_allow_html=True)
choice = st.sidebar.radio("NAVIGATE", ["🏠 MAIN MENU", "🔐 ADMIN ACCESS", "👨‍🎓 STUDENT RESULT"])

# --- PAGE 1: MAIN MENU ---
if choice == "🏠 MAIN MENU":
    st.markdown("<h1 style='text-align: center;'>Welcome to Elite Management System</h1>", unsafe_allow_html=True)
    st.markdown("""
    <div class='premium-card' style='text-align: center;'>
        <h3>Choose your portal from the left navigation bar to get started.</h3>
        <p>This system provides real-time result tracking and advanced administrative controls.</p>
    </div>
    """, unsafe_allow_html=True)
    st.image("https://img.freepik.com/free-vector/connected-world-concept-illustration_114360-3027.jpg", use_container_width=True)

# --- PAGE 2: ADMIN SECTION ---
elif choice == "🔐 ADMIN ACCESS":
    st.title("🛡️ Admin Secure Terminal")
    
    if 'admin_auth' not in st.session_state: st.session_state.admin_auth = False

    if not st.session_state.admin_auth:
        with st.form("Login"):
            u = st.text_input("Username", placeholder="admin")
            p = st.text_input("Password", type="password")
            if st.form_submit_button("UNSEAL ACCESS"):
                if u == ADMIN_USERNAME and p == ADMIN_PASSWORD:
                    st.session_state.admin_auth = True
                    st.rerun()
                else: st.error("Access Denied: Invalid Credentials")
    else:
        st.sidebar.button("LOGOUT", on_click=lambda: st.session_state.update({"admin_auth": False}))
        
        tab1, tab2, tab3, tab4 = st.tabs(["📝 Add Record", "📊 View Database", "🔄 Update Marks", "📥 Export"])

        with tab1:
            st.subheader("Register New Entry")
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
                
                if st.form_submit_button("SUBMIT DATA"):
                    if r and n:
                        data[r] = {"name": n, "class": cl, "marks": marks, "date": str(datetime.now().date())}
                        save_data(data)
                        st.snow()
                        st.success(f"Record for {n} Encrypted & Saved!")
                    else: st.warning("Critical fields missing!")

        with tab2:
            st.subheader("Global Student Database")
            if data:
                db_list = [{"Roll": r, "Name": i['name'], "Class": i['class'], "Total": sum(i['marks'].values())} for r, i in data.items()]
                st.dataframe(pd.DataFrame(db_list), use_container_width=True)
            else: st.info("No records found in the encrypted vault.")

        with tab3:
            st.subheader("Modification Interface")
            u_roll = st.text_input("Target Roll Number")
            if u_roll in data:
                with st.form("upd"):
                    st.info(f"Modifying: {data[u_roll]['name']}")
                    new_m = {sub: st.number_input(sub, 0, 100, value=data[u_roll]['marks'].get(sub, 0)) for sub in SUBJECTS}
                    if st.form_submit_button("OVERWRITE MARKS"):
                        data[u_roll]['marks'] = new_m
                        save_data(data)
                        st.success("Buffer Updated!")
            elif u_roll: st.error("Target Not Found")

        with tab4:
            st.subheader("Data Extraction")
            if data:
                export_list = []
                for r, info in data.items():
                    row = {"Roll": r, "Name": info['name'], "Class": info['class']}
                    row.update(info['marks'])
                    t = sum(info['marks'].values())
                    p = (t/700)*100
                    row.update({"Total": t, "Percentage": f"{p:.2f}%", "Grade": get_grade_styles(p)[0]})
                    export_list.append(row)
                st.download_button("GENERATE CSV", pd.DataFrame(export_list).to_csv(index=False).encode('utf-8'), "Elite_Data.csv")

# --- PAGE 3: STUDENT SECTION ---
elif choice == "👨‍🎓 STUDENT RESULT":
    st.title("🎓 Digital Marksheet Portal")
    roll = st.text_input("Enter Encrypted Roll Number", placeholder="e.g. 1001")
    
    if st.button("RETRIEVE RESULT"):
        if roll in data:
            s = data[roll]
            st.balloons()
            
            st.markdown(f"""
            <div class='premium-card'>
                <h1 style='margin:0; color:#00d2ff;'>{s['name']}</h1>
                <p>Class: {s['class']} | Session: 2024-25</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Table
            df_m = pd.DataFrame(list(s['marks'].items()), columns=["Subject", "Obtained"])
            st.table(df_m)
            
            total = sum(s['marks'].values())
            perc = (total/TOTAL_MARKS)*100
            grade, color = get_grade_styles(perc)
            
            st.divider()
            c1, c2, c3 = st.columns(3)
            c1.metric("TOTAL MARKS", f"{total} / 700")
            c2.metric("PERC (%)", f"{perc:.2f}%")
            st.markdown(f"<div class='premium-card' style='text-align:center; border-color:{color};'><h2 style='color:{color}; margin:0;'>{grade}</h2></div>", unsafe_allow_html=True)
        else:
            st.error("Roll Number not verified in system.")
