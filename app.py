import streamlit as st
import pandas as pd
import datetime
import uuid
import os
import plotly.express as px

# --- APP CONFIGURATION ---
st.set_page_config(page_title="Community Donation Hub", layout="wide", initial_sidebar_state="expanded")

# CSS for Receipt Styling
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Arabic:wght@400;700&display=swap');
    .main { background-color: #f8fafc; }
    .urdu-text { font-family: 'Noto Sans Arabic', sans-serif; direction: rtl; text-align: right; }
    .receipt-card {
        background: white; padding: 25px; border-radius: 10px;
        border: 1px solid #ddd; font-family: sans-serif;
    }
    .metric-card {
        background: white; padding: 20px; border-radius: 10px; border-left: 5px solid #059669;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    </style>
""", unsafe_allow_html=True)

# --- DATA STORAGE ---
DB_FILE = "donations.csv"
def load_data():
    if os.path.exists(DB_FILE): return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=['id', 'receipt_no', 'donor_name', 'amount', 'category', 'region', 'timestamp'])

def save_data(df): df.to_csv(DB_FILE, index=False)

if 'data' not in st.session_state: st.session_state.data = load_data()

# --- SIDEBAR: ENTRY ---
with st.sidebar:
    st.markdown('<h2 class="urdu-text">نیا ریکارڈ</h2>', unsafe_allow_html=True)
    with st.form("donation_form", clear_on_submit=True):
        donor_name = st.text_input("Name")
        amount = st.number_input("Amount", min_value=0, step=500)
        category = st.selectbox("Category", ["Zakat", "Fitra", "Monthly Chanda", "Atiyah"])
        region = st.selectbox("Region", ["5 NO", "J-1", "J-AREA", "4 NO"])
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
                st.success("Saved!")

# --- DASHBOARD ---
st.title("Donation Hub")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Total", f"Rs. {st.session_state.data['amount'].sum():,}")
m2.metric("Zakat", f"Rs. {st.session_state.data[st.session_state.data['category']=='Zakat']['amount'].sum():,}")
m3.metric("Monthly", f"Rs. {st.session_state.data[st.session_state.data['category']=='Monthly Chanda']['amount'].sum():,}")
m4.metric("Fitra", f"Rs. {st.session_state.data[st.session_state.data['category']=='Fitra']['amount'].sum():,}")

# --- RECORDS & PRINT ---
st.markdown("---")
if not st.session_state.data.empty:
    for _, row in st.session_state.data.iloc[::-1].iterrows():
        with st.expander(f"📄 {row['receipt_no']} - {row['donor_name']}"):
            # Receipt HTML
            receipt_html = f"""
            <div id="q-receipt" style="border:2px solid #000; padding:20px; width:300px; font-family:Arial;">
                <h2 style="text-align:center;">RECEIPT</h2>
                <hr>
                <p><b>No:</b> {row['receipt_no']}</p>
                <p><b>Name:</b> {row['donor_name']}</p>
                <p><b>Amount:</b> Rs. {row['amount']}</p>
                <p><b>Category:</b> {row['category']}</p>
                <p><b>Date:</b> {row['timestamp']}</p>
            </div>
            """
            st.markdown(receipt_html, unsafe_allow_html=True)
            
            # Simple Download Button
            st.download_button(
                label="Download Receipt as Text",
                data=f"RECEIPT\nNo: {row['receipt_no']}\nName: {row['donor_name']}\nAmount: {row['amount']}\nCategory: {row['category']}\nDate: {row['timestamp']}",
                file_name=f"receipt_{row['receipt_no']}.txt",
                mime="text/plain"
            )
