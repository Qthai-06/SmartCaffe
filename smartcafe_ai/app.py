# pyrefly: ignore [missing-import]
import os
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

try:
    from PIL import Image
except Exception:
    Image = None

try:
    from ultralytics import YOLO
except Exception:
    YOLO = None

st.set_page_config(
    page_title="SmartCafé AI",
    page_icon="☕",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ===================== DATA =====================
DEFAULT_INVENTORY = pd.DataFrame([
    {"Tên hàng": "Chai cà phê size M", "Số lượng": 12, "Đơn vị": "chai", "Mức tối thiểu": 8},
    {"Tên hàng": "Chai cà phê size L", "Số lượng": 8, "Đơn vị": "chai", "Mức tối thiểu": 6},
    {"Tên hàng": "Bịch cà phê 1kg", "Số lượng": 3, "Đơn vị": "bịch", "Mức tối thiểu": 5},
    {"Tên hàng": "Siro dâu", "Số lượng": 5, "Đơn vị": "chai", "Mức tối thiểu": 4},
    {"Tên hàng": "Ly nhựa", "Số lượng": 120, "Đơn vị": "cái", "Mức tối thiểu": 80},
])

CLASS_MAP = {
    "coffee_bottle_m": "Chai cà phê size M",
    "coffee_bottle_l": "Chai cà phê size L",
    "coffee_bag_1kg": "Bịch cà phê 1kg",
    "siro_dau": "Siro dâu",
    "plastic_cup": "Ly nhựa",
    "phe binh": "Chai cà phê size M",
    "Cà phê xay": "Bịch cà phê 1kg",
    "Ly giấy": "Ly nhựa",
    "Ly nhựa": "Ly nhựa",
    "Sữa đặc": "Siro dâu",
}

if "inventory" not in st.session_state:
    st.session_state.inventory = DEFAULT_INVENTORY.copy()
if "detected_counts" not in st.session_state:
    st.session_state.detected_counts = {}
if "last_image" not in st.session_state:
    st.session_state.last_image = None
if "last_annotated" not in st.session_state:
    st.session_state.last_annotated = None
if "sales_today" not in st.session_state:
    st.session_state.sales_today = 245
if "forecast_today" not in st.session_state:
    st.session_state.forecast_today = 280


# ===================== LOGIN =====================
USERS = {
    "admin": {"password": "admin123", "name": "Admin", "role": "Quản lý"},
    "staff": {"password": "staff123", "name": "Nhân viên", "role": "Nhân viên kho"},
}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "current_user" not in st.session_state:
    st.session_state.current_user = None

def logout():
    st.session_state.logged_in = False
    st.session_state.current_user = None
    st.rerun()

def render_login_page():
    st.markdown("""
    <style>
    .login-wrap{min-height:78vh;display:flex;align-items:center;justify-content:center;}
    .login-card{width:430px;background:rgba(255,255,255,.94);border:1px solid #efe6dc;border-radius:24px;padding:34px 34px 28px;box-shadow:0 24px 60px rgba(65,35,12,.13);}
    .login-logo{text-align:center;font-size:58px;margin-bottom:6px;}
    .login-title{text-align:center;font-size:32px;font-weight:900;color:#2b170c;margin:0;}
    .login-sub{text-align:center;color:#7b6b5d;margin:8px 0 26px;font-size:15px;}
    .hint{background:#fff7e9;border:1px solid #efd4a9;border-radius:12px;padding:12px 14px;margin-top:16px;color:#6b4b2f;font-size:14px;}
    </style>
    <div class="login-wrap"><div class="login-card">
      <div class="login-logo">☕</div>
      <h1 class="login-title">SmartCafé AI</h1>
      <p class="login-sub">Đăng nhập hệ thống quản lý kho & dự báo</p>
    """, unsafe_allow_html=True)

    with st.form("login_form", clear_on_submit=False):
        username = st.text_input("Tên đăng nhập", placeholder="admin")
        password = st.text_input("Mật khẩu", type="password", placeholder="admin123")
        submitted = st.form_submit_button("Đăng nhập", use_container_width=True)

    if submitted:
        user = USERS.get(username.strip())
        if user and password == user["password"]:
            st.session_state.logged_in = True
            st.session_state.current_user = {
                "username": username.strip(),
                "name": user["name"],
                "role": user["role"],
            }
            st.success("Đăng nhập thành công!")
            st.rerun()
        else:
            st.error("Sai tên đăng nhập hoặc mật khẩu.")

    st.markdown("""
      <div class="hint"><b>Tài khoản test:</b><br>Admin: <code>admin</code> / <code>admin123</code><br>Nhân viên: <code>staff</code> / <code>staff123</code></div>
    </div></div>
    """, unsafe_allow_html=True)

if not st.session_state.logged_in:
    render_login_page()
    st.stop()

current_user = st.session_state.current_user or {"name":"Admin", "role":"Quản lý", "username":"admin"}

# ===================== CSS =====================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
*{font-family:'Inter',sans-serif;}
.stApp{background:linear-gradient(120deg,#fffaf2 0%,#fbf6ee 55%,#fffefd 100%);}
.block-container{padding-top:1.4rem;padding-bottom:2rem;max-width:1480px;}
#MainMenu, footer, header{visibility:hidden;}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#3b2415 0%,#211106 100%);border-right:0;}
[data-testid="stSidebar"] *{color:#fff;}
[data-testid="stSidebar"] .block-container{padding:1.4rem 1rem;}
.logo-box{padding:18px 14px 22px 14px;}
.logo-cup{font-size:46px;line-height:1;margin-bottom:8px;}
.logo-title{font-size:29px;font-weight:800;letter-spacing:-1px;margin:0;color:white;}
.logo-sub{font-size:15px;color:#ead9c9!important;margin-top:6px;}
.nav-item{display:flex;align-items:center;gap:12px;padding:14px 16px;margin:8px 0;border-radius:12px;color:#f8efe5!important;font-weight:600;}
.nav-active{background:rgba(217,167,115,.45);box-shadow:inset 0 0 0 1px rgba(255,255,255,.08);}
.side-card{border:1px solid rgba(255,255,255,.14);border-radius:14px;padding:18px;background:rgba(255,255,255,.06);margin-top:40px;}
.side-card p{font-size:14px;color:#ead9c9!important;line-height:1.6;margin:10px 0 0;}
.topbar{display:flex;align-items:center;justify-content:space-between;margin-bottom:20px;}
.hello h1{font-size:28px;font-weight:800;margin:0;color:#1f1b18;letter-spacing:-.4px;}
.hello p{font-size:15px;color:#6f6258;margin:8px 0 0;}
.user-tools{display:flex;align-items:center;gap:14px;}
.date-pill{display:flex;align-items:center;gap:12px;border:1px solid #ddd3c7;background:#fff;border-radius:12px;padding:12px 18px;font-weight:700;color:#2c2621;box-shadow:0 8px 22px rgba(70,45,20,.05);}
.bell{width:44px;height:44px;border-radius:50%;display:grid;place-items:center;background:#fff;border:1px solid #eadfd4;position:relative;font-size:22px;}
.badge{position:absolute;top:-4px;right:-2px;background:#d83d33;color:#fff;border-radius:50%;font-size:11px;font-weight:800;width:20px;height:20px;display:grid;place-items:center;}
.admin{display:flex;align-items:center;gap:10px;}.avatar{width:46px;height:46px;border-radius:50%;display:grid;place-items:center;background:#efe0cc;font-size:25px;}
.kpi-card{background:rgba(255,255,255,.88);border:1px solid #efe6dc;border-radius:14px;padding:22px 20px;box-shadow:0 10px 28px rgba(74,43,18,.06);min-height:116px;display:flex;align-items:center;gap:18px;}
.kpi-icon{width:64px;height:64px;border-radius:50%;display:grid;place-items:center;font-size:30px;font-weight:800;}.kpi-title{font-size:15px;font-weight:700;color:#3d342d;margin-bottom:4px;}.kpi-value{font-size:36px;font-weight:800;letter-spacing:-1px;line-height:1;color:#2b211a;}.kpi-value span{font-size:15px;font-weight:600;color:#6f6258;letter-spacing:0;margin-left:4px;}.kpi-note{font-size:13px;color:#75695e;margin-top:8px;}
.bg-orange{background:#fff0dd;color:#9b5b17}.bg-green{background:#e8f8ee;color:#13944c}.bg-blue{background:#eaf3ff;color:#2259a8}.bg-purple{background:#f2eafe;color:#8753c7}
.panel{background:rgba(255,255,255,.94);border:1px solid #efe6dc;border-radius:16px;padding:18px 20px;box-shadow:0 10px 28px rgba(74,43,18,.055);margin-top:14px;}
.panel-title{display:flex;align-items:center;gap:10px;font-size:20px;font-weight:800;color:#25201c;margin-bottom:14px;}
.stButton>button{border-radius:10px;font-weight:800;border:0;background:linear-gradient(135deg,#6d3f20,#3e2413);color:white;padding:.65rem 1rem;}
.stDownloadButton>button{border-radius:10px;font-weight:800;}
.ai-box{border-radius:10px;padding:16px 18px;margin:12px 0;border:1px solid;font-size:15px;line-height:1.45;}.ai-yellow{background:#fff9e7;border-color:#f1dd9f}.ai-red{background:#fff0ee;border-color:#f3c2bc}.ai-green{background:#eef9f1;border-color:#c4e6cd}.ai-box b{display:block;margin-bottom:4px;color:#2b211a;}
[data-testid="stMetric"]{background:#fff;border:1px solid #efe6dc;border-radius:14px;padding:15px;}
</style>
""", unsafe_allow_html=True)

# ===================== HELPERS =====================
def get_inventory_with_status(df):
    out = df.copy()
    out["Trạng thái"] = out.apply(lambda r: "Sắp hết" if int(r["Số lượng"]) < int(r["Mức tối thiểu"]) else "Ổn định", axis=1)
    return out

@st.cache_resource(show_spinner=False)
def load_model(model_path):
    if YOLO is None:
        return None
    if not os.path.exists(model_path):
        return None
    return YOLO(model_path)

def predict_image(image, conf, model_path):
    model = load_model(model_path)
    if model is None:
        return {}, None, "Không tìm thấy YOLO hoặc model. Hãy kiểm tra ultralytics và file best.pt/yolo11n.pt."
    results = model(image, conf=conf, verbose=False)
    result = results[0]
    counts = {}
    names = result.names
    if result.boxes is not None:
        for cls_id in result.boxes.cls.tolist():
            raw_name = names[int(cls_id)]
            item_name = CLASS_MAP.get(raw_name, raw_name)
            counts[item_name] = counts.get(item_name, 0) + 1
    annotated = result.plot()
    return counts, annotated, None

def update_inventory_from_counts(counts):
    df = st.session_state.inventory.copy()
    for item, qty in counts.items():
        if item in df["Tên hàng"].values:
            df.loc[df["Tên hàng"] == item, "Số lượng"] = int(qty)
        else:
            new_row = pd.DataFrame([{"Tên hàng": item, "Số lượng": int(qty), "Đơn vị": "cái", "Mức tối thiểu": 1}])
            df = pd.concat([df, new_row], ignore_index=True)
    st.session_state.inventory = df

# ===================== SIDEBAR =====================
with st.sidebar:
    st.markdown("""
    <div class="logo-box">
        <div class="logo-cup">☕</div>
        <h2 class="logo-title">SmartCafé AI</h2>
        <div class="logo-sub">AI Quản lý Kho & Dự báo</div>
    </div>
    """, unsafe_allow_html=True)
    page = st.radio("", ["🏠 Trang chủ", "📷 Chụp & Đếm hàng", "📦 Tồn kho", "🤖 AI Advisor", "📄 Xuất báo cáo"], label_visibility="collapsed")
    st.markdown(f"<div style='margin-top:14px;color:#ead9c9'>👤 Đang đăng nhập: <b>{current_user['name']}</b></div>", unsafe_allow_html=True)
    if st.button("🚪 Đăng xuất", use_container_width=True):
        logout()
    st.markdown("---")
    st.markdown("### ⚙️ Cài đặt hệ thống")
    conf = st.slider("Độ nhạy AI (Confidence)", 0.05, 0.95, 0.40, 0.05)
    default_model = "data/models/best.pt" if os.path.exists("data/models/best.pt") else "yolo11n.pt"
    model_path = st.text_input("Đường dẫn model", default_model)
    st.markdown("""
    <div class="side-card">
        <b>SmartCafé AI</b>
        <p>Tiết kiệm thời gian<br>Giảm lãng phí<br>Tăng hiệu quả</p>
        <small>Version 1.0.0</small>
    </div>
    """, unsafe_allow_html=True)

# ===================== HEADER =====================
now = datetime.now()
st.markdown(f"""
<div class="topbar">
    <div class="hello">
        <h1>Xin chào, {current_user['name']}! 👋</h1>
        <p>Đây là tổng quan hoạt động của quán cà phê hôm nay.</p>
    </div>
    <div class="user-tools">
        <div class="date-pill">🗓️ <div>{now.strftime('%d/%m/%Y')}<br><span style="font-weight:600">{now.strftime('%H:%M')}</span></div></div>
        <div class="bell">🔔<span class="badge">3</span></div>
        <div class="admin"><div class="avatar">👤</div><div><b>{current_user['name']}</b><small>{current_user['role']}</small></div>⌄</div>
    </div>
</div>
""", unsafe_allow_html=True)

inv_status = get_inventory_with_status(st.session_state.inventory)
total_qty = int(inv_status["Số lượng"].sum())
low_count = int((inv_status["Trạng thái"] == "Sắp hết").sum())

k1, k2, k3, k4 = st.columns(4)
with k1:
    st.markdown(f'<div class="kpi-card"><div class="kpi-icon bg-orange">📦</div><div><div class="kpi-title">Tổng số lượng hàng</div><div class="kpi-value">{total_qty} <span>đơn vị</span></div><div class="kpi-note">Tất cả nguyên liệu</div></div></div>', unsafe_allow_html=True)
with k2:
    st.markdown(f'<div class="kpi-card"><div class="kpi-icon bg-green">🧊</div><div><div class="kpi-title" style="color:#14934c">Mặt hàng sắp hết</div><div class="kpi-value" style="color:#14934c">{low_count} <span>mặt hàng</span></div><div class="kpi-note">Cần nhập sớm</div></div></div>', unsafe_allow_html=True)
with k3:
    st.markdown(f'<div class="kpi-card"><div class="kpi-icon bg-blue">☕</div><div><div class="kpi-title">Số ly bán hôm nay</div><div class="kpi-value" style="color:#1d4f98">{st.session_state.sales_today} <span>ly</span></div><div class="kpi-note">Cập nhật tự động</div></div></div>', unsafe_allow_html=True)
with k4:
    st.markdown(f'<div class="kpi-card"><div class="kpi-icon bg-purple">↗️</div><div><div class="kpi-title">Dự báo hôm nay</div><div class="kpi-value" style="color:#8753c7">{st.session_state.forecast_today} <span>ly</span></div><div class="kpi-note">Dự báo tổng ngày</div></div></div>', unsafe_allow_html=True)

# ===================== PAGES =====================
def render_capture_panel():
    st.markdown('<div class="panel"><div class="panel-title">📷 Chụp ảnh & AI đếm hàng</div>', unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["📤 Tải ảnh lên", "📸 Chụp camera"])
    image_source = None
    with tab1:
        uploaded = st.file_uploader("Chọn ảnh kho hàng để AI phân tích", type=["jpg", "jpeg", "png"])
        if uploaded and Image:
            image_source = Image.open(uploaded).convert("RGB")
            st.image(image_source, caption="Ảnh đã tải lên", use_container_width=True)
    with tab2:
        cam = st.camera_input("Chụp ảnh trực tiếp")
        if cam and Image:
            image_source = Image.open(cam).convert("RGB")
            st.image(image_source, caption="Ảnh từ camera", use_container_width=True)

    c1, c2, c3 = st.columns([1,1,1.2])
    with c1:
        analyze = st.button("🤖 Phân tích bằng AI", use_container_width=True)
    with c2:
        confirm = st.button("✅ Xác nhận nhập kho", use_container_width=True)
    with c3:
        if st.button("🔄 Reset kết quả", use_container_width=True):
            st.session_state.detected_counts = {}
            st.session_state.last_annotated = None
            st.rerun()

    if analyze:
        if image_source is None:
            st.warning("Bạn cần tải ảnh hoặc chụp ảnh trước.")
        else:
            counts, annotated, err = predict_image(image_source, conf, model_path)
            if err:
                st.error(err)
            else:
                st.session_state.detected_counts = counts
                st.session_state.last_annotated = annotated
                st.success("AI đã phân tích xong.")

    if st.session_state.last_annotated is not None:
        st.image(st.session_state.last_annotated, caption="Kết quả nhận diện", use_container_width=True)
    if st.session_state.detected_counts:
        st.write("**Kết quả đếm được:**")
        st.dataframe(pd.DataFrame(st.session_state.detected_counts.items(), columns=["Mặt hàng", "Số lượng"]), use_container_width=True, hide_index=True)

    if confirm:
        if st.session_state.detected_counts:
            update_inventory_from_counts(st.session_state.detected_counts)
            st.success("Đã cập nhật tồn kho theo kết quả AI.")
        else:
            st.warning("Chưa có kết quả AI để cập nhật.")
    st.markdown('</div>', unsafe_allow_html=True)

def render_inventory_panel():
    st.markdown('<div class="panel"><div class="panel-title">📋 Tồn kho hiện tại</div>', unsafe_allow_html=True)
    edited = st.data_editor(
        st.session_state.inventory,
        use_container_width=True,
        hide_index=True,
        num_rows="dynamic",
        column_config={
            "Số lượng": st.column_config.NumberColumn(min_value=0, step=1),
            "Mức tối thiểu": st.column_config.NumberColumn(min_value=0, step=1),
        },
    )
    st.session_state.inventory = edited
    st.dataframe(get_inventory_with_status(st.session_state.inventory), use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)

def render_forecast_panel():
    st.markdown('<div class="panel"><div class="panel-title">🗃️ Dự báo số ly bán 7 ngày tới</div>', unsafe_allow_html=True)
    forecast = pd.DataFrame({
        "Ngày": ["Thứ 4\n21/05", "Thứ 5\n22/05", "Hôm nay\n23/05", "Thứ 7\n24/05", "CN\n25/05", "Thứ 2\n26/05", "Thứ 3\n27/05"],
        "Số ly": [210, 180, st.session_state.sales_today, 220, 250, st.session_state.forecast_today, 300],
    })
    st.bar_chart(forecast.set_index("Ngày"))
    st.markdown('</div>', unsafe_allow_html=True)

def render_advisor_panel():
    low_df = get_inventory_with_status(st.session_state.inventory)
    low_items = low_df[low_df["Trạng thái"] == "Sắp hết"]
    st.markdown('<div class="panel"><div class="panel-title">🤖 AI Advisor - Gợi ý thông minh</div>', unsafe_allow_html=True)
    st.session_state.sales_today = st.number_input("Số ly đã bán hôm nay", min_value=0, value=int(st.session_state.sales_today), step=1)
    st.session_state.forecast_today = st.number_input("Dự báo số ly hôm nay", min_value=0, value=int(st.session_state.forecast_today), step=1)
    st.markdown('<div class="ai-box ai-yellow">💡 <b>Hôm nay lượng khách có thể tăng vào buổi tối.</b>Nên chuẩn bị thêm nguyên liệu bán chạy để tránh thiếu hàng.</div>', unsafe_allow_html=True)
    if not low_items.empty:
        for _, r in low_items.iterrows():
            need = int(r["Mức tối thiểu"] - r["Số lượng"])
            st.markdown(f'<div class="ai-box ai-red">🛒 <b>{r["Tên hàng"]} đang sắp hết.</b>Nên nhập thêm ít nhất {need} {r["Đơn vị"]} để đạt mức tối thiểu.</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="ai-box ai-green">✅ <b>Tồn kho đang ổn định.</b>Chưa có mặt hàng nào thấp hơn mức tối thiểu.</div>', unsafe_allow_html=True)
    risk = max(0, min(100, 100 - low_count * 18))
    st.markdown(f'<div class="ai-box ai-green">✅ <b>Đủ bán cuối tuần: {risk}%</b> Nên kiểm tra lại các mặt hàng bán chạy trước giờ cao điểm.</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

def render_report_panel():
    st.markdown('<div class="panel"><div class="panel-title">📄 Xuất báo cáo</div>', unsafe_allow_html=True)
    report = get_inventory_with_status(st.session_state.inventory)
    st.dataframe(report, use_container_width=True, hide_index=True)
    csv = report.to_csv(index=False).encode("utf-8-sig")
    st.download_button("⬇️ Tải báo cáo CSV", csv, file_name=f"smartcafe_report_{datetime.now().strftime('%Y%m%d_%H%M')}.csv", mime="text/csv")
    st.markdown('</div>', unsafe_allow_html=True)

if page == "🏠 Trang chủ":
    left, right = st.columns([1.03, 1])
    with left:
        render_capture_panel()
        render_forecast_panel()
    with right:
        st.markdown('<div class="panel"><div class="panel-title">📋 Tồn kho hiện tại</div>', unsafe_allow_html=True)
        st.dataframe(get_inventory_with_status(st.session_state.inventory), use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)
        render_advisor_panel()
elif page == "📷 Chụp & Đếm hàng":
    render_capture_panel()
elif page == "📦 Tồn kho":
    render_inventory_panel()
elif page == "🤖 AI Advisor":
    render_advisor_panel()
elif page == "📄 Xuất báo cáo":
    render_report_panel()
