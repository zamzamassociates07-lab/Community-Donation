import streamlit as st
import pandas as pd
import datetime
import uuid
import os

# --- APP CONFIGURATION ---
st.set_page_config(page_title="Community Donation Hub", layout="wide")

# Custom CSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Arabic:wght@400;700&display=swap');
    .urdu-text { font-family: 'Noto Sans Arabic', sans-serif; direction: rtl; text-align: right; }
    .receipt-card {
        background: white; padding: 25px; border-radius: 12px;
        border: 1px solid #eee; color: black !important;
    }
    .stButton>button { border-radius: 6px; width: 100%; }
    .delete-btn>button { background-color: #ef4444 !important; color: white !important; }
    
    @media print {
        header, footer, .sidebar, [data-testid="stHeader"], [data-testid="stSidebar"], .stButton, .stExpanderDetails div:not(.printable-receipt) {
            display: none !important;
        }
        .printable-receipt { display: block !important; position: fixed; left: 0; top: 0; width: 100%; background: white; z-index: 9999; }
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

if 'data' not in st.session_state:
    st.session_state.data = load_data()

# --- SIDEBAR: NEW ENTRY ---
with st.sidebar:
    st.markdown('<h2 class="urdu-text">نیا ریکارڈ</h2>', unsafe_allow_html=True)
    with st.form("donation_form", clear_on_submit=True):
        donor_name = st.text_input("Donor Name")
        amount = st.number_input("Amount", min_value=0, step=500)
        category = st.selectbox("Category", ["Zakat", "Fitra", "Monthly Chanda", "Atiyah", "General"])
        region = st.selectbox("Region", ["5 NO", "J-1", "J-AREA", "4 NO", "Other"])
        if st.form_submit_button("Save"):
            if donor_name and amount > 0:
                new_entry = {
                    'id': str(uuid.uuid4()), 
                    'receipt_no': f"REC-{datetime.datetime.now().strftime('%y%m%d')}-{len(st.session_state.data)+1}",
                    'donor_name': donor_name, 'amount': amount, 'category': category, 
                    'region': region, 'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                }
                st.session_state.data = pd.concat([st.session_state.data, pd.DataFrame([new_entry])], ignore_index=True)
                save_data(st.session_state.data)
                st.rerun()

    if st.button("🔄 Refresh App"):
        st.rerun()

# --- DASHBOARD ---
st.markdown('<h1 class="urdu-text">ڈونیشن ڈیش بورڈ</h1>', unsafe_allow_html=True)

# Metrics
cols = st.columns(4)
cols[0].metric("Total Collection", f"Rs. {st.session_state.data['amount'].sum():,}")
cols[1].metric("Zakat", f"Rs. {st.session_state.data[st.session_state.data['category']=='Zakat']['amount'].sum():,}")
cols[2].metric("Monthly", f"Rs. {st.session_state.data[st.session_state.data['category']=='Monthly Chanda']['amount'].sum():,}")
cols[3].metric("Fitra", f"Rs. {st.session_state.data[st.session_state.data['category']=='Fitra']['amount'].sum():,}")

# --- RECORDS ---
st.markdown("---")
if not st.session_state.data.empty:
    for index, row in st.session_state.data.iloc[::-1].iterrows():
        with st.expander(f"📄 {row['receipt_no']} - {row['donor_name']}"):
            col_rec, col_opt = st.columns([2, 1])
            
            with col_rec:
                receipt_html = f"""
                <div class="printable-receipt">
                    <div class="receipt-card">
                        <h3 style="text-align:center; color:#059669;">COMMUNITY RECEIPT</h3>
                        <hr>
                        <p><b>Receipt No:</b> {row['receipt_no']}<br>
                        <b>Donor:</b> {row['donor_name']}<br>
                        <b>Amount:</b> Rs. {row['amount']:,}<br>
                        <b>Category:</b> {row['category']}<br>
                        <b>Date:</b> {row['timestamp']}</p>
                    </div>
                </div>
                """
                st.markdown(receipt_html, unsafe_allow_html=True)

            with col_opt:
                # 1. Print/PDF Button
                if st.button(f"Print PDF", key=f"p-{row['id']}"):
                    st.markdown("<script>window.print();</script>", unsafe_allow_html=True)
                
                # 2. Professional WhatsApp Message
                wa_text = (
                    f"*COMMUNITY DONATION RECEIPT*%0A"
                    f"---------------------------%0A"
                    f"*Receipt No:* {row['receipt_no']}%0A"
                    f"*Donor Name:* {row['donor_name']}%0A"
                    f"*Amount:* Rs. {row['amount']:,}%0A"
                    f"*Category:* {row['category']}%0A"
                    f"*Date:* {row['timestamp']}%0A"
                    f"---------------------------%0A"
                    f"Thank you for your donation!"
                )
                st.markdown(f'<a href="https://wa.me/?text={wa_text}" target="_blank" style="text-decoration:none;"><div style="background:#25D366; color:white; padding:10px; border-radius:6px; text-align:center; margin-bottom:10px;">Send to WhatsApp</div></a>', unsafe_allow_html=True)

                # 3. Delete Option
                st.markdown('<div class="delete-btn">', unsafe_allow_html=True)
                if st.button(f"Delete Entry", key=f"d-{row['id']}"):
                    st.session_state.data = st.session_state.data.drop(index)
                    save_data(st.session_state.data)
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
