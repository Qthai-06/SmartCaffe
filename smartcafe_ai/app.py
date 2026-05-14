import streamlit as st
import pandas as pd
import datetime
import cv2
import os
import logging
import numpy as np
from PIL import Image
from src.vision import SmartCafeVision
from src.auth import authenticate, get_auth_users
from src.database import save_inventory as save_inventory_snapshot, get_latest_inventory, init_database
import streamlit.components.v1 as components
from ui.page_inventory import render as render_inventory_page
from ui.page_advisor import render as render_advisor_page

logger = logging.getLogger(__name__)

st.set_page_config(
    page_title="SmartCafé AI",
    page_icon="☕",
    layout="wide"
)

# ================= DATA =================
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)
CSV_FILE_PATH = os.path.join(DATA_DIR, "inventory.csv")

ITEMS = ["cafe_hat", "cafe_xay", "ly_giay", "ly_nhua", "sua_dac"]

DISPLAY_NAMES = {
    "cafe_hat": "Cà phê hạt",
    "cafe_xay": "Cà phê xay",
    "ly_giay": "Ly giấy",
    "ly_nhua": "Ly nhựa",
    "sua_dac": "Sữa đặc"
}

UNITS = {
    "cafe_hat": "bịch",
    "cafe_xay": "bịch",
    "ly_giay": "cái",
    "ly_nhua": "cái",
    "sua_dac": "lon"
}

MIN_STOCK = {
    "cafe_hat": 5,
    "cafe_xay": 5,
    "ly_giay": 80,
    "ly_nhua": 80,
    "sua_dac": 4
}

# Dữ liệu ban đầu rỗng = 0
for item in ITEMS:
    if item not in st.session_state:
        st.session_state[item] = 0

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_name" not in st.session_state:
    st.session_state.user_name = "Admin"
if "user_role" not in st.session_state:
    st.session_state.user_role = "admin"

init_database()
latest_inventory = get_latest_inventory()
for item in ITEMS:
    st.session_state[item] = latest_inventory.get(item, st.session_state.get(item, 0))

@st.cache_resource
def load_ai():
    try:
        return SmartCafeVision()
    except (FileNotFoundError, ValueError, RuntimeError) as ex:
        logger.error("Không thể nạp model AI: %s", ex)
        return None

vision_core = load_ai()

# ================= CSS =================
st.markdown("""
<style>
.stApp {
    background: #ffffff;
}

.block-container {
    padding: 0;
    max-width: 100%;
}

[data-testid="stSidebar"] {
    background: #ffffff;
    border-right: 1px solid #eee;
}

.sidebar-logo {
    text-align: center;
    padding: 25px 10px 35px;
}

.logo-icon {
    font-size: 58px;
    color: #ff5a00;
}

.logo-title {
    font-size: 28px;
    font-weight: 800;
    color: #ff5a00;
}

.main-wrap {
    padding: 30px 36px;
}

.login-wrap {
    max-width: 620px;
    margin: 90px auto;
    text-align: center;
}

.login-title {
    font-size: 46px;
    font-weight: 800;
    color: #ff5a00;
}

.login-sub {
    color: #6b7280;
    font-size: 20px;
    margin-bottom: 35px;
}

.login-card {
    border: 1px solid #e5e7eb;
    border-radius: 18px;
    padding: 35px;
    box-shadow: 0 8px 28px rgba(0,0,0,0.05);
    background: white;
    text-align: left;
}

.header {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.hello {
    font-size: 32px;
    font-weight: 800;
}

.date-box {
    border: 1px solid #e5e7eb;
    padding: 14px 24px;
    border-radius: 12px;
    font-size: 16px;
    background: white;
    min-width: 300px;
    text-align: center;
}

.card {
    border: 1px solid #e5e7eb;
    border-radius: 18px;
    padding: 24px;
    background: white;
    box-shadow: 0 8px 24px rgba(0,0,0,0.04);
}

.metric-card {
    border: 1px solid #e5e7eb;
    border-radius: 18px;
    padding: 25px 30px;
    background: white;
    box-shadow: 0 8px 24px rgba(0,0,0,0.04);
    min-height: 120px;
}

.metric-flex {
    display: flex;
    align-items: center;
    gap: 22px;
}

.metric-icon {
    width: 70px;
    height: 70px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 34px;
}

.orange {
    background: linear-gradient(135deg, #ff6a00, #ff4b00);
    color: white;
}

.green {
    background: linear-gradient(135deg, #10b981, #059669);
    color: white;
}

.blue {
    background: linear-gradient(135deg, #3b82f6, #2563eb);
    color: white;
}

.metric-title {
    font-size: 18px;
    color: #374151;
}

.metric-number {
    font-size: 42px;
    font-weight: 800;
    color: #111827;
}

.metric-unit {
    font-size: 18px;
    color: #6b7280;
    margin-left: 8px;
}

.section-title {
    font-size: 25px;
    font-weight: 800;
    margin-bottom: 20px;
}

.advice-row {
    font-size: 18px;
    padding: 16px 0;
}

.stButton > button {
    border-radius: 10px;
    font-weight: 700;
}
</style>
""", unsafe_allow_html=True)

# ================= FUNCTIONS =================
def live_clock_html():
    return """
    <div id="clock" style="
        font-family: Arial, sans-serif;
        font-size: 16px;
        font-weight: 700;
        color: #111827;
    "></div>

    <script>
    function updateClock() {
        const now = new Date();

        const weekdays = [
            "Chủ nhật", "Thứ 2", "Thứ 3", "Thứ 4",
            "Thứ 5", "Thứ 6", "Thứ 7"
        ];

        const day = weekdays[now.getDay()];
        const date = String(now.getDate()).padStart(2, '0');
        const month = String(now.getMonth() + 1).padStart(2, '0');
        const year = now.getFullYear();

        const hour = String(now.getHours()).padStart(2, '0');
        const minute = String(now.getMinutes()).padStart(2, '0');
        const second = String(now.getSeconds()).padStart(2, '0');

        document.getElementById("clock").innerHTML =
            "📅 " + day + ", " + date + "/" + month + "/" + year +
            "<br>⏰ " + hour + ":" + minute + ":" + second;
    }

    updateClock();
    setInterval(updateClock, 1000);
    </script>
    """

def inventory_table():
    rows = []

    for item in ITEMS:
        qty = int(st.session_state[item])
        min_qty = MIN_STOCK[item]

        if qty == 0:
            status = "Chưa cập nhật"
        elif qty < min_qty:
            status = "Sắp hết"
        else:
            status = "Ổn định"

        rows.append({
            "Tên hàng": DISPLAY_NAMES[item],
            "Số lượng": qty,
            "Đơn vị": UNITS[item],
            "Mức tối thiểu": min_qty,
            "Trạng thái": status
        })

    return pd.DataFrame(rows)

def save_inventory():
    payload = {item: int(st.session_state.get(item, 0) or 0) for item in ITEMS}
    previous = get_latest_inventory()
    save_inventory_snapshot(
        inventory_counts=payload,
        source="app_main",
        actor=st.session_state.get("user_name", "staff"),
        previous_counts=previous,
        reason="inventory_save",
    )

def process_image(image_file):
    if vision_core is None:
        raise RuntimeError("Model AI chưa sẵn sàng.")

    image = Image.open(image_file).convert("RGB")
    frame = np.array(image)

    if len(frame.shape) == 3:
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    else:
        frame_bgr = frame

    processed_frame, counts = vision_core.process_frame(frame_bgr)
    processed_rgb = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)

    for item, count in counts.items():
        if item in st.session_state:
            st.session_state[item] = count

    return processed_rgb, counts

def forecast_data():
    today = datetime.datetime.now()
    data = []
    values = [210, 180, 190, 220, 250, 280, 300]

    for i in range(7):
        d = today + datetime.timedelta(days=i)
        data.append({
            "Ngày": d.strftime("%d/%m"),
            "Dự báo số ly": values[i]
        })

    return pd.DataFrame(data)

# ================= LOGIN =================
if not st.session_state.logged_in:
    st.markdown("""
    <div class="login-wrap">
        <div class="login-title">☕ SmartCafé AI</div>
        <div class="login-sub">Đăng nhập hệ thống quản lý kho & dự báo</div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.2, 1])

    with col2:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)

        email = st.text_input("Email", placeholder="Nhập email của bạn")
        password = st.text_input("Mật khẩu", type="password", placeholder="Nhập mật khẩu")
        st.checkbox("Ghi nhớ đăng nhập")

        if st.button("Đăng nhập", type="primary", use_container_width=True):
            user = authenticate(email, password)
            if user:
                st.session_state.logged_in = True
                st.session_state.user_name = user.get("name", "Admin")
                st.session_state.user_role = user.get("role", "staff")
                st.rerun()
            else:
                st.error("Sai email hoặc mật khẩu!")

        st.markdown("</div>", unsafe_allow_html=True)
        if not get_auth_users():
            st.warning("Chưa cấu hình tài khoản. Vui lòng đặt SMARTCAFE_AUTH_USERS_JSON hoặc SMARTCAFE_ADMIN_EMAIL/PASSWORD.")

    st.stop()

# ================= SIDEBAR =================
with st.sidebar:
    st.markdown("""
    <div class="sidebar-logo">
        <div class="logo-icon">☕</div>
        <div class="logo-title">SmartCafé AI</div>
    </div>
    """, unsafe_allow_html=True)

    menu = st.radio(
        "Menu",
        ["Trang chủ", "Kiểm kê", "Tồn kho", "AI Advisor", "Xuất báo cáo"],
        label_visibility="collapsed"
    )

    st.markdown("<br><br><br>", unsafe_allow_html=True)

    if st.button("Đăng xuất", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

# ================= MAIN =================
st.markdown('<div class="main-wrap">', unsafe_allow_html=True)

# Header
h1, h2 = st.columns([3, 1])
user_name = st.session_state.get("user_name", "Admin")

with h1:
    st.markdown(f"""
    <div class="hello">Xin chào, {user_name}! 👋</div>
    <p style="color:#6b7280;">Đây là tổng quan hoạt động của quán cà phê hôm nay.</p>
    """, unsafe_allow_html=True)

with h2:
    st.markdown('<div class="date-box">', unsafe_allow_html=True)
    components.html(live_clock_html(), height=70)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Metrics
inv_df = inventory_table()
total_qty = int(inv_df["Số lượng"].sum())
low_count = len(inv_df[inv_df["Trạng thái"] == "Sắp hết"])
today_forecast = int(forecast_data().iloc[0]["Dự báo số ly"])

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-flex">
            <div class="metric-icon orange">📦</div>
            <div>
                <div class="metric-title">Tổng hàng</div>
                <span class="metric-number">{total_qty}</span>
                <span class="metric-unit">đơn vị</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-flex">
            <div class="metric-icon green">⚠️</div>
            <div>
                <div class="metric-title">Mặt hàng sắp hết</div>
                <span class="metric-number">{low_count}</span>
                <span class="metric-unit">mặt hàng</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-flex">
            <div class="metric-icon blue">📈</div>
            <div>
                <div class="metric-title">Dự báo hôm nay</div>
                <span class="metric-number">{today_forecast}</span>
                <span class="metric-unit">ly</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ================= PAGES =================
if menu == "Trang chủ":
    left, right = st.columns([1, 1.9])

    with left:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Kiểm kê bằng AI</div>', unsafe_allow_html=True)

        image_file = st.file_uploader("Chọn ảnh từ máy", type=["jpg", "jpeg", "png"])

        if image_file:
            try:
                result_img, counts = process_image(image_file)
                st.image(result_img, caption="Kết quả AI nhận diện", use_container_width=True)
            except (OSError, ValueError, RuntimeError) as ex:
                logger.exception("Lỗi xử lý AI ở Trang chủ")
                st.error(f"Lỗi xử lý AI: {ex}")
                counts = {}

            if counts and st.button("Lưu kho", type="primary", use_container_width=True):
                save_inventory()
                st.success("Đã lưu dữ liệu tồn kho.")

        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Tồn kho hiện tại</div>', unsafe_allow_html=True)
        st.dataframe(inventory_table(), use_container_width=True, hide_index=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    b1, b2 = st.columns([1.1, 1])

    with b1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Dự báo 7 ngày</div>', unsafe_allow_html=True)
        st.line_chart(forecast_data().set_index("Ngày"))
        st.markdown("</div>", unsafe_allow_html=True)

    with b2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Gợi ý AI</div>', unsafe_allow_html=True)

        if total_qty == 0:
            st.markdown("""
            <div class="advice-row">ℹ️ Chưa có dữ liệu tồn kho. Hãy kiểm kê bằng AI trước.</div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="advice-row">💡 Hôm nay dự báo khoảng {today_forecast} ly.</div>
            <div class="advice-row">🛒 Có {low_count} mặt hàng sắp hết. Nên nhập bổ sung.</div>
            <div class="advice-row">✅ Hệ thống đã có dữ liệu để đưa ra gợi ý.</div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

elif menu == "Kiểm kê":
    render_inventory_page()

elif menu == "Tồn kho":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Tồn kho hiện tại</div>', unsafe_allow_html=True)

    df = inventory_table()
    st.dataframe(df, use_container_width=True, hide_index=True)

    if total_qty > 0:
        st.bar_chart(df.set_index("Tên hàng")["Số lượng"])
    else:
        st.info("Chưa có dữ liệu tồn kho. Hãy kiểm kê bằng AI trước.")

    st.markdown("</div>", unsafe_allow_html=True)

elif menu == "AI Advisor":
    render_advisor_page()

elif menu == "Xuất báo cáo":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Xuất báo cáo</div>', unsafe_allow_html=True)

    try:
        df = pd.read_csv(CSV_FILE_PATH)
        st.dataframe(df, use_container_width=True, hide_index=True)

        csv = df.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            "Tải báo cáo CSV",
            data=csv,
            file_name="bao_cao_smartcafe.csv",
            mime="text/csv",
            type="primary",
            use_container_width=True
        )
    except FileNotFoundError:
        st.info("Chưa có dữ liệu kiểm kê.")

    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)
