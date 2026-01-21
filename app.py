import streamlit as st
import pandas as pd
import datetime
import uuid
import os
import plotly.express as px

# --- APP CONFIGURATION ---
st.set_page_config(page_title="Community Donation Hub", layout="wide", initial_sidebar_state="expanded")

# Custom CSS for Aesthetics and Urdu Support
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Arabic:wght@400;700&display=swap');
    
    .main { background-color: #f1f5f9; }
    .urdu-text { font-family: 'Noto Sans Arabic', sans-serif; direction: rtl; text-align: right; }
    .stButton>button { width: 100%; border-radius: 12px; height: 3em; font-weight: bold; }
    .receipt-card {
        background: white; padding: 40px; border-radius: 20px;
        border: 1px solid #eee; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1);
        font-family: sans-serif;
    }
    @media print {
        .no-print { display: none !important; }
        .receipt-card { box-shadow: none; border: 1px solid #000; }
    }
    </style>
""", unsafe_allow_html=True)

# --- DATA PERSISTENCE ---
DB_FILE = "donations.csv"

def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=['id', 'receipt_no', 'donor_name', 'amount', 'category', 'region', 'timestamp'])

def save_data(df):
    df.to_csv(DB_FILE, index=False)

# --- LOGIC FUNCTIONS ---
def generate_receipt_no(region, count):
    date_str = datetime.datetime.now().strftime("%Y%m%d")
    region_codes = {"5 NO": "5N", "J-1": "J1", "J-AREA": "JA", "4 NO": "4N"}
    r_code = region_codes.get(region, "GEN")
    seq = str(count + 1).zfill(7)
    return f"{date_str}-{r_code}-{seq}"

# --- APP STATE ---
if 'data' not in st.session_state:
    st.session_state.data = load_data()

# --- SIDEBAR: ENTRY FORM ---
with st.sidebar:
    st.markdown('<div class="urdu-text" style="font-size: 24px; font-weight: bold; color: #059669;">ڈونیشن ہب</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    st.markdown('<p class="urdu-text">نئی انٹری درج کریں</p>', unsafe_allow_html=True)
    
    with st.form("donation_form", clear_on_submit=True):
        donor_name = st.text_input("Donor Name / نام")
        amount = st.number_input("Amount / رقم", min_value=0, step=100)
        category = st.selectbox("Category / مقصد", ["Zakat", "Fitra", "Atiyah", "Monthly Chanda"])
        region = st.selectbox("Region / علاقہ", ["5 NO", "J-1", "J-AREA", "4 NO"])
        
        submitted = st.form_submit_button("Save Entry (محفوظ کریں)")
        
        if submitted:
            if donor_name and amount > 0:
                new_id = str(uuid.uuid4())
                r_no = generate_receipt_no(region, len(st.session_state.data))
                new_entry = {
                    'id': new_id,
                    'receipt_no': r_no,
                    'donor_name': donor_name,
                    'amount': amount,
                    'category': category,
                    'region': region,
                    'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                st.session_state.data = pd.concat([st.session_state.data, pd.DataFrame([new_entry])], ignore_index=True)
                save_data(st.session_state.data)
                st.success("Data Saved Successfully!")
            else:
                st.error("Please fill all fields.")

# --- MAIN DASHBOARD ---
st.title("Community Donation Dashboard")
st.markdown("---")

# Metrics Row
col1, col2, col3 = st.columns(3)
total_amt = st.session_state.data['amount'].sum()
total_rec = len(st.session_state.data)
zakat_amt = st.session_state.data[st.session_state.data['category'] == 'Zakat']['amount'].sum()

with col1:
    st.metric("Total Collection", f"Rs. {total_amt:,}")
with col2:
    st.metric("Total Receipts", total_rec)
with col3:
    st.metric("Zakat Pool", f"Rs. {zakat_amt:,}")

st.markdown("### Financial Analytics")
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    if not st.session_state.data.empty:
        fig_cat = px.bar(st.session_state.data.groupby('category')['amount'].sum().reset_index(), 
                         x='category', y='amount', title="Collection by Category",
                         color_discrete_sequence=['#059669'])
        st.plotly_chart(fig_cat, use_container_width=True)
    else:
        st.info("No data for charts")

with chart_col2:
    if not st.session_state.data.empty:
        reg_summary = st.session_state.data.groupby('region')['amount'].sum().reset_index()
        fig_reg = px.pie(reg_summary, values='amount', names='region', title="Regional Breakdown",
                         hole=0.4, color_discrete_sequence=px.colors.qualitative.Safe)
        st.plotly_chart(fig_reg, use_container_width=True)
        
        # Regional Breakdown List
        for index, row in reg_summary.iterrows():
            st.markdown(f"**{row['region']}:** Rs. {row['amount']:,}")

# --- TRANSACTION LOG ---
st.markdown("---")
st.markdown('<h3 class="urdu-text">ڈونیشن ریکارڈ لاگ</h3>', unsafe_allow_html=True)

if not st.session_state.data.empty:
    # Reverse the dataframe to show latest entries first
    display_df = st.session_state.data.iloc[::-1]
    
    for _, row in display_df.iterrows():
        with st.expander(f"📄 {row['receipt_no']} | {row['donor_name']} | Rs. {row['amount']:,}"):
            c1, c2 = st.columns([3, 1])
            with c1:
                st.write(f"**Category:** {row['category']} | **Region:** {row['region']} | **Date:** {row['timestamp']}")
            with c2:
                if st.button("View Receipt", key=row['id']):
                    st.session_state.selected_receipt = row
                    st.rerun()

# --- RECEIPT MODAL / OVERLAY ---
if 'selected_receipt' in st.session_state and st.session_state.selected_receipt is not None:
    receipt = st.session_state.selected_receipt
    
    st.markdown("---")
    st.markdown(f"""
        <div class="receipt-card" id="printable-receipt">
            <div style="text-align: center; border-bottom: 2px solid #059669; padding-bottom: 20px; margin-bottom: 20px;">
                <h1 style="margin:0; color: #065f46;">COMMUNITY DONATION HUB</h1>
                <p style="margin:0; font-weight: bold; color: #059669; letter-spacing: 2px;">OFFICIAL RECEIPT</p>
            </div>
            <table style="width: 100%; border-collapse: collapse;">
                <tr>
                    <td style="padding: 10px 0; color: #666; font-size: 12px;">RECEIPT NO:</td>
                    <td style="text-align: right; font-family: monospace; font-weight: bold;">{receipt['receipt_no']}</td>
                </tr>
                <tr>
                    <td style="padding: 10px 0; color: #666; font-size: 12px;">DATE:</td>
                    <td style="text-align: right; font-weight: bold;">{receipt['timestamp']}</td>
                </tr>
                <tr style="border-top: 1px solid #eee;">
                    <td style="padding: 15px 0; font-weight: bold;">DONOR NAME:</td>
                    <td style="text-align: right; font-size: 18px; font-weight: 900;">{receipt['donor_name']}</td>
                </tr>
                <tr>
                    <td style="padding: 10px 0; font-weight: bold;">PURPOSE:</td>
                    <td style="text-align: right;"><span style="background: #ecfdf5; color: #065f46; padding: 5px 15px; border-radius: 50px; font-size: 12px; font-weight: bold;">{receipt['category']}</span></td>
                </tr>
                <tr>
                    <td style="padding: 10px 0; font-weight: bold;">REGION:</td>
                    <td style="text-align: right; font-weight: bold;">{receipt['region']}</td>
                </tr>
                <tr style="border-top: 2px dashed #059669;">
                    <td style="padding: 20px 0; font-size: 20px; font-weight: bold; color: #065f46;">TOTAL AMOUNT:</td>
                    <td style="text-align: right; font-size: 28px; font-weight: 900; color: #059669;">Rs. {receipt['amount']:,}</td>
                </tr>
            </table>
            <div style="text-align: center; margin-top: 30px; border-top: 1px solid #eee; padding-top: 20px;">
                <p class="urdu-text" style="color: #065f46; font-size: 14px;">اللہ تعالیٰ آپ کا عطیہ قبول فرمائے۔ آمین</p>
                <p style="font-size: 10px; color: #aaa;">Digital Verification ID: {receipt['id'][:16]}</p>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Action Buttons for Receipt
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.button("Print (Ctrl+P)", on_click=lambda: None) # Browser print handles this
    with col_b:
        whatsapp_text = f"*Donation Receipt*%0A*No:* {receipt['receipt_no']}%0A*Donor:* {receipt['donor_name']}%0A*Amount:* Rs.{receipt['amount']:,}%0A*Category:* {receipt['category']}%0A*Region:* {receipt['region']}"
        st.markdown(f'<a href="https://wa.me/?text={whatsapp_text}" target="_blank" style="text-decoration:none;"><div style="background:#25D366; color:white; padding:10px; border-radius:12px; text-align:center; font-weight:bold;">Share on WhatsApp</div></a>', unsafe_allow_html=True)
    with col_c:
        if st.button("Close Receipt"):
            st.session_state.selected_receipt = None
            st.rerun()

# Empty state footer
if st.session_state.data.empty:
    st.info("Welcome! Please use the sidebar to log your first donation.")
