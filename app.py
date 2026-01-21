import pandas as pd
import datetime
import uuid
import os
import plotly.express as px

# --- APP CONFIGURATION ---
st.set_page_config(page_title="Community Donation Hub", layout="wide", initial_sidebar_state="expanded")

# Custom CSS for Professional Look and Urdu Support
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Arabic:wght@400;700&display=swap');
    
    .main { background-color: #f8fafc; }
    .urdu-text { font-family: 'Noto Sans Arabic', sans-serif; direction: rtl; text-align: right; }
    .stButton>button { border-radius: 8px; font-weight: bold; background-color: #059669; color: white; }
    .receipt-card {
        background: #ffffff; padding: 30px; border-radius: 15px;
        border: 2px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
    }
    .metric-card {
        background: white; padding: 20px; border-radius: 10px; border-left: 5px solid #059669;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    @media print {
        .no-print { display: none !important; }
        .receipt-card { border: none; box-shadow: none; }
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

# --- RECEIPT GENERATOR ---
def generate_receipt_no(region, count):
    date_str = datetime.datetime.now().strftime("%Y%m%d")
    r_code = region[:2].upper()
    seq = str(count + 1).zfill(5)
    return f"REC-{date_str}-{r_code}-{seq}"

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
                r_no = generate_receipt_no(region, len(st.session_state.data))
                new_entry = {
                    'id': new_id, 'receipt_no': r_no, 'donor_name': donor_name,
                    'amount': amount, 'category': category, 'region': region,
                    'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                }
                st.session_state.data = pd.concat([st.session_state.data, pd.DataFrame([new_entry])], ignore_index=True)
                save_data(st.session_state.data)
                st.balloons()
                st.success("Record Saved!")

# --- MAIN DASHBOARD ---
st.markdown('<h1 class="urdu-text" style="color:#065f46;">کمیونٹی ڈونیشن ڈیش بورڈ</h1>', unsafe_allow_html=True)

# Updated Metrics Row
m1, m2, m3, m4 = st.columns(4)
with m1:
    st.markdown(f'<div class="metric-card"><h4>Total Collection</h4><h3>Rs. {st.session_state.data["amount"].sum():,}</h3></div>', unsafe_allow_html=True)
with m2:
    zakat = st.session_state.data[st.session_state.data["category"]=="Zakat"]["amount"].sum()
    st.markdown(f'<div class="metric-card"><h4>Zakat Pool</h4><h3>Rs. {zakat:,}</h3></div>', unsafe_allow_html=True)
with m3:
    monthly = st.session_state.data[st.session_state.data["category"]=="Monthly Chanda"]["amount"].sum()
    st.markdown(f'<div class="metric-card"><h4>Monthly Pool</h4><h3>Rs. {monthly:,}</h3></div>', unsafe_allow_html=True)
with m4:
    fitra = st.session_state.data[st.session_state.data["category"]=="Fitra"]["amount"].sum()
    st.markdown(f'<div class="metric-card"><h4>Fitra Pool</h4><h3>Rs. {fitra:,}</h3></div>', unsafe_allow_html=True)

# Charts
st.markdown("### Visual Analytics")
c1, c2 = st.columns(2)
if not st.session_state.data.empty:
    with c1:
        fig1 = px.pie(st.session_state.data, values='amount', names='category', title="By Category", hole=.4)
        st.plotly_chart(fig1, use_container_width=True)
    with c2:
        fig2 = px.bar(st.session_state.data.groupby('region')['amount'].sum().reset_index(), x='region', y='amount', title="By Region", color='region')
        st.plotly_chart(fig2, use_container_width=True)

# --- DATA TABLE & RECEIPTS ---
st.markdown("---")
st.markdown('<h3 class="urdu-text">حالیہ ریکارڈز</h3>', unsafe_allow_html=True)

if not st.session_state.data.empty:
    for _, row in st.session_state.data.iloc[::-1].iterrows():
        with st.expander(f"📄 {row['receipt_no']} - {row['donor_name']} (Rs. {row['amount']})"):
            col_left, col_right = st.columns([2, 1])
            
            receipt_html = f"""
                <div class="receipt-card" id="receipt-{row['id']}">
                    <h4 style="color:#059669; text-align:center;">OFFICIAL RECEIPT</h4>
                    <hr>
                    <p><b>Receipt No:</b> {row['receipt_no']}</p>
                    <p><b>Donor:</b> {row['donor_name']}</p>
                    <p><b>Amount:</b> Rs. {row['amount']:,}</p>
                    <p><b>Category:</b> {row['category']} | <b>Region:</b> {row['region']}</p>
                    <p style="font-size:10px; color:gray;">Date: {row['timestamp']}</p>
                </div>
            """
            
            with col_left:
                st.markdown(receipt_html, unsafe_allow_html=True)
            
            with col_right:
                # Download/Print Option
                st.markdown('<p class="urdu-text">آپشنز</p>', unsafe_allow_html=True)
                if st.button(f"Download PDF / Print", key=f"print-{row['id']}"):
                    st.info("براہ کرم کھلنے والی ونڈو میں 'Save as PDF' منتخب کریں۔")
                    st.markdown(f"<script>window.print();</script>", unsafe_allow_html=True)
                
                whatsapp_msg = f"Thank you {row['donor_name']}! Receipt: {row['receipt_no']} | Amount: Rs.{row['amount']} received for {row['category']}."
                st.markdown(f'<a href="https://wa.me/?text={whatsapp_msg}" target="_blank" style="text-decoration:none;"><div style="background:#25D366; color:white; padding:10px; border-radius:8px; text-align:center; margin-top:10px;">Share on WhatsApp</div></a>', unsafe_allow_html=True)
