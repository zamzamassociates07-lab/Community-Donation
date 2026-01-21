import streamlit as st
import pandas as pd
import google.generativeai as genai  # AI Studio کی لائبریری

# --- یہاں اپنی API Key ڈالیں ---
MY_API_KEY = "AIzaSyBbSokKGsjbacPFVRTo21Lqyha69sbbqRc"
genai.configure(AIzaSyBbSokKGsjbacPFVRTo21Lqyha69sbbqRcY)
model = genai.GenerativeModel('gemini-1.5-flash')

st.set_page_config(page_title="Bradri Donation", layout="wide")
st.title("💰 چار علاقہ جات - اسمارٹ کھاتہ")

def load_data():
    try:
        return pd.read_csv("data.csv")
    except:
        return pd.DataFrame(columns=["تاریخ", "علاقہ", "خزانچی", "رقم"])

data = load_data()

# سائیڈ بار فارم
with st.sidebar:
    st.header("نئی انٹری کریں")
    area = st.selectbox("علاقہ منتخب کریں", ["جے ایریا", "علاقہ 2", "علاقہ 3", "علاقہ 4"])
    treasurer = st.text_input("خزانچی کا نام")
    amount = st.number_input("رقم", min_value=0)
    
    if st.button("ڈیٹا محفوظ کریں"):
        new_data = pd.DataFrame([[pd.Timestamp.now().strftime("%Y-%m-%d %H:%M"), area, treasurer, amount]], 
                                columns=["تاریخ", "علاقہ", "خزانچی", "رقم"])
        updated_data = pd.concat([data, new_data], ignore_index=True)
        updated_data.to_csv("data.csv", index=False)
        st.success(f"{area} کا ڈیٹا محفوظ ہو گیا!")
        st.rerun()

# ڈیش بورڈ (حساب کتاب)
st.subheader("مجموعی رپورٹ")
cols = st.columns(4)
areas = ["جے ایریا", "علاقہ 2", "علاقہ 3", "علاقہ 4"]

for i, a in enumerate(areas):
    total = data[data['علاقہ'] == a]['رقم'].sum()
    cols[i].metric(a, f"{total} Rs")

st.divider()

# AI سے سوال پوچھیں
st.subheader("🤖 AI خزانچی سے مشورہ کریں")
user_q = st.text_input("اپنے حساب کتاب کے بارے میں کچھ پوچھیں (مثلاً: سب سے زیادہ رقم کس نے جمع کی؟)")
if user_q and not data.empty:
    prompt = f"یہ میرا مالیاتی ڈیٹا ہے: {data.to_string()}. سوال: {user_q}"
    response = model.generate_content(prompt)
    st.info(response.text)

st.dataframe(data, use_container_width=True)
