import streamlit as st
import pandas as pd
import datetime
import uuid
import os
import plotly.express as px

# --- APP CONFIGURATION ---
st.set_page_config(page_title="Community Donation Hub", layout="wide", initial_sidebar_state="expanded")

# Custom CSS for Professional Look, Urdu Support and Printing
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Arabic:wght@400;700&display=swap');
    
    .main { background-color: #f8fafc; }
    .urdu-text { font-family: 'Noto Sans Arabic', sans-serif; direction: rtl; text-align: right; }
    .stButton>button { border-radius: 8px; font-weight: bold; background-color: #059669; color: white; }
    
    /* Receipt Design */
    .receipt-card {
        background: #ffffff; padding: 30px; border-radius: 15px;
        border: 2px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
        max-width: 500px; margin: auto;
    }
    .metric-card {
        background: white; padding: 20px; border-radius: 10px; border-left: 5px solid #059669;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }

    /* PDF/Print Preview Optimization */
    @media print {
        body * { visibility: hidden; }
        .receipt-card, .receipt-card * { visibility: visible; }
        .receipt-card {
            position: absolute; left: 0; top: 0; width: 100%;
            border: 1px solid #000; box-shadow: none;
        }
        .no-print { display: none !important; }
    }
    </style>
""", unsafe_allow_html=True)

# --- DATA STORAGE ---
DB_FILE = "donations.csv"

def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=['id', 'receipt_no', 'donor_name', 'amount', 'category', 'region', 'timestamp'])

def save_data(df):
    df.to_csv(DB_FILE, index=False)

# --- INITIALIZE STATE ---
if 'data' not in st.session_state:
    st.session_state.data = load_data()

# --- SIDEBAR: NEW ENTRY ---
with st.sidebar:
    st.markdown('<h2 class="urdu-text">نیا ریکارڈ درج کریں</h2>', unsafe_allow_html=True)
    with st.form("donation_form", clear_on_submit=True):
        donor_name = st.text_input("Donor Name (نام)")
        amount = st.number_input("Amount (رقم)", min_value=0, step=500)
        category = st.selectbox("Category (مقصد)", ["Zakat", "Fitra", "Monthly Chanda", "Atiyah", "General"])
        region = st.selectbox("Region (علاقہ)", ["5 NO", "J-1", "J-AREA", "4 NO", "Other"])
        
        submitted = st.form_submit_button("Save Data (محفوظ کریں)")
        
        if submitted:
            if donor_name and amount > 0:
                new_id = str(uuid.uuid4())
                r_no = f"REC-{datetime.datetime.now().strftime('%y%m%d')}-{str(len(st.session_state.data)+1).zfill(4)}"
                new_entry = {
                    'id': new_id, 'receipt_no': r_no, 'donor_name': donor_name,
                    'amount': amount, 'category': category, 'region': region,
                    'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                }
                st.session_state.data = pd.concat([st.session_state.data, pd.DataFrame([new_entry])], ignore_index=True)
                save_data(st.session_state.data)
                st.balloons()

# --- MAIN DASHBOARD ---
st.markdown('<h1 class="urdu-text" style="color:#065f46;">کمیونٹی ڈونیشن ڈیش بورڈ</h1>', unsafe_allow_html=True)

# Metrics Row (Pool word removed)
m1, m2, m3, m4 = st.columns(4)
with m1:
    st.markdown(f'<div class="metric-card"><h4>Total Collection</h4><h3>Rs. {st.session_state.data["amount"].sum():,}</h3></div>', unsafe_allow_html=True)
with m2:
    zakat = st.session_state.data[st.session_state.data["category"]=="Zakat"]["amount"].sum()
    st.markdown(f'<div class="metric-card"><h4>Zakat</h4><h3>Rs. {zakat:,}</h3></div>', unsafe_allow_html=True)
with m3:
    monthly = st.session_state.data[st.session_state.data["category"]=="Monthly Chanda"]["amount"].sum()
    st.markdown(f'<div class="metric-card"><h4>Monthly</h4><h3>Rs. {monthly:,}</h3></div>', unsafe_allow_html=True)
with m4:
    fitra = st.session_state.data[st.session_state.data["category"]=="Fitra"]["amount"].sum()
    st.markdown(f'<div class="metric-card"><h4>Fitra</h4><h3>Rs. {fitra:,}</h3></div>', unsafe_allow_html=True)

# --- TRANSACTION LOG & PRINT ---
st.markdown("---")
st.markdown('<h3 class="urdu-text">حالیہ ریکارڈز اور رسید</h3>', unsafe_allow_html=True)

if not st.session_state.data.empty:
    for _, row in st.session_state.data.iloc[::-1].iterrows():
        with st.expander(f"📄 {row['receipt_no']} - {row['donor_name']} (Rs. {row['amount']})"):
            col_rec, col_opt = st.columns([2, 1])
            
            with col_rec:
                st.markdown(f"""
                <div class="receipt-card">
                    <h3 style="color:#059669; text-align:center; margin-bottom:0;">COMMUNITY DONATION</h3>
                    <p style="text-align:center; font-size:12px; color:gray;">OFFICIAL RECEIPT</p>
                    <hr>
                    <table style="width:100%; border:none;">
                        <tr><td><b>Receipt No:</b></td><td style="text-align:right;">{row['receipt_no']}</td></tr>
                        <tr><td><b>Donor Name:</b></td><td style="text-align:right;">{row['donor_name']}</td></tr>
                        <tr><td><b>Amount:</b></td><td style="text-align:right; font-size:20px; color:#059669;"><b>Rs. {row['amount']:,}</b></td></tr>
                        <tr><td><b>Category:</b></td><td style="text-align:right;">{row['category']}</td></tr>
                        <tr><td><b>Region:</b></td><td style="text-align:right;">{row['region']}</td></tr>
                        <tr><td><b>Date:</b></td><td style="text-align:right;">{row['timestamp']}</td></tr>
                    </table>
                    <hr>
                    <p style="text-align:center; font-size:12px; color:gray;">Thank you for your donation!</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col_opt:
                if st.button(f"Print / Save PDF", key=f"btn-{row['id']}"):
                    st.markdown("<script>window.print();</script>", unsafe_allow_html=True)
                
                wa_url = f"https://wa.me/?text=Receipt:{row['receipt_no']}%0ADonor:{row['donor_name']}%0AAmount:Rs.{row['amount']}"
                st.markdown(f'<a href="{wa_url}" target="_blank" style="text-decoration:none;"><div style="background:#25D366; color:white; padding:10px; border-radius:8px; text-align:center; margin-top:10px;">WhatsApp Share</div></a>', unsafe_allow_html=True)
