import streamlit as st
import requests
import time
import math

# --- ตั้งค่าหน้าเว็บ ---
st.set_page_config(page_title="AI Football Pro", layout="centered")

# ==========================================
# 1. จัดการความลับ (API KEY)
# ==========================================
# เราจะดึง Key จากระบบหลังบ้าน (Secrets) โดยที่ลูกค้าไม่เห็น
# แต่ถ้าเปิดในคอมตัวเอง แล้วยังไม่ได้ตั้งค่า Secrets ให้ใช้คีย์สำรองไปก่อน
try:
    API_KEY = st.secrets["API_KEY"]
except:
    # ใส่ Key ของคุณตรงนี้ชั่วคราวเพื่อเทสในเครื่อง (อย่าลืมลบก่อนขึ้น GitHub ถ้าเป็น Repo สาธารณะ)
    API_KEY = "ใส่_API_KEY_ของคุณตรงนี้_เพื่อเทสในเครื่อง"

# ==========================================
# 2. จำลองฐานข้อมูลลูกค้า
# ==========================================
users_db = {
    "user1": {"password": "123", "credits": 50},
    "vip":   {"password": "999", "credits": 1000}
}

# ... (ส่วน Login เหมือนเดิม) ...
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.user_credits = 0

def login():
    username = st.session_state.input_user
    password = st.session_state.input_pass
    if username in users_db and users_db[username]['password'] == password:
        st.session_state.logged_in = True
        st.session_state.username = username
        st.session_state.user_credits = users_db[username]['credits']
    else:
        st.error("❌ ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง")

def logout():
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 เข้าสู่ระบบ")
    st.text_input("Username", key="input_user")
    st.text_input("Password", type="password", key="input_pass")
    st.button("เข้าสู่ระบบ", on_click=login)
    st.info("💡 ทดลองใช้: User: `user1` / Pass: `123`")
    st.stop()

# ==========================================
# 3. หน้าจอหลัก (ไม่มีช่องใส่ Key แล้ว!)
# ==========================================
st.title("⚽ AI Football Prediction")

col1, col2 = st.columns([2, 1])
with col1:
    st.success(f"👤 ผู้ใช้งาน: {st.session_state.username}")
with col2:
    credit_color = "green" if st.session_state.user_credits > 20 else "red"
    st.markdown(f"💰 เครดิต: **:{credit_color}[{st.session_state.user_credits}]**")

if st.button("ออกจากระบบ"):
    logout()
    st.rerun()

st.divider()

st.subheader("🚀 เริ่มวิเคราะห์แมตช์")

# --- ตรงนี้คือจุดเปลี่ยน! เราลบช่อง input API Key ออกแล้ว ---
# ใช้ตัวแปร API_KEY ที่เราประกาศไว้ข้างบนแทน

fixture_id = st.text_input("Fixture ID (เช่น 1035043)")

col_a, col_b = st.columns(2)
with col_a:
    handicap = st.number_input("Handicap", value=0.5, step=0.25)
with col_b:
    away_xg = st.number_input("Away xG", value=0.7)

if st.button("🔮 วิเคราะห์ผล (ใช้ 10 เครดิต)", type="primary"):
    if st.session_state.user_credits < 10:
        st.error("⛔ เครดิตของคุณไม่พอ! กรุณาเติมเงิน")
    else:
        if not fixture_id:
            st.warning("กรุณาใส่ Fixture ID")
        else:
            with st.spinner('กำลังเชื่อมต่อ AI...'):
                # --- ยิง API จริงๆ โดยใช้ Key ลับ ---
                url = f"https://v3.football.api-sports.io/fixtures/lineups?fixture={fixture_id}"
                headers = {"x-apisports-key": API_KEY}
                
                try:
                    # จำลองการโหลดนิดนึง
                    time.sleep(1) 
                    response = requests.get(url, headers=headers)
                    data = response.json()
                    
                    # (ในโค้ดจริงต้องเอา Logic คำนวณมาใส่ตรงนี้)
                    # เพื่อความง่าย ขอจำลองผลลัพธ์ก่อน
                    if "errors" in data and data["errors"]:
                        st.error(f"API Error: {data['errors']}")
                    else:
                        st.session_state.user_credits -= 10
                        st.success("✅ วิเคราะห์สำเร็จ!")
                        st.metric(label="โอกาสเจ้าบ้านชนะ", value="52.42%", delta="เสี่ยงวัดใจ")
                        st.toast(f"หัก 10 เครดิต (คงเหลือ: {st.session_state.user_credits})")
                        
                except Exception as e:
                    st.error(f"เกิดข้อผิดพลาด: {e}")