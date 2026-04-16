# ☕ SmartCafé AI

Hệ thống quản lý kho hàng thông minh dành cho quán cà phê, ứng dụng **Thị giác máy tính (Computer Vision)** và **Dự báo chuỗi thời gian (Time Series Forecasting)**.

---

## ✨ Tính năng chính

- **📸 Chụp & Đếm hàng** — Sử dụng YOLOv8 để nhận diện và đếm số lượng hàng tồn kho từ ảnh chụp hoặc camera trực tiếp.
- **🤖 AI Advisor** — Dự báo nhu cầu tiêu thụ bằng Facebook Prophet, hiển thị biểu đồ tương tác qua Plotly và đưa ra gợi ý nhập hàng.
- **🗄️ Quản lý tồn kho** — Lưu trữ toàn bộ dữ liệu hàng hóa và lịch sử giao dịch trên SQLite.

---

## 🛠️ Công nghệ sử dụng

| Thành phần | Công nghệ |
|---|---|
| Giao diện (Frontend) | Streamlit |
| Thị giác máy tính | Ultralytics YOLOv8 |
| Dự báo nhu cầu | Facebook Prophet |
| Cơ sở dữ liệu | SQLite |
| Xử lý & Trực quan hóa dữ liệu | Pandas, OpenCV, Plotly |

---

## 📁 Cấu trúc dự án

```
smartcafe_ai/
├── requirements.txt          # Danh sách thư viện cần cài đặt
├── README.md                 # Tài liệu tổng quan dự án
├── app.py                    # Điểm khởi chạy ứng dụng Streamlit
├── config.py                 # Biến cấu hình (đường dẫn DB, model, v.v.)
│
├── data/
│   ├── db/                   # Thư mục chứa file SQLite database
│   ├── sample_images/        # Thư mục chứa ảnh mẫu để kiểm thử
│   └── models/               # Thư mục chứa file trọng số YOLOv8 (.pt)
│
├── src/                      # Xử lý logic nghiệp vụ cốt lõi
│   ├── __init__.py
│   ├── vision.py             # Module nhận diện vật thể bằng YOLOv8
│   ├── forecast.py           # Module dự báo chuỗi thời gian bằng Prophet
│   └── database.py           # Module thao tác CRUD với SQLite
│
└── ui/                       # Giao diện Streamlit
    ├── __init__.py
    ├── page_inventory.py     # Trang "Chụp & Đếm hàng"
    ├── page_advisor.py       # Trang "AI Advisor" (Dự báo & Biểu đồ)
    └── components.py         # Các thành phần UI tái sử dụng
```

---

## 🚀 Hướng dẫn cài đặt & chạy

### 1. Cài đặt thư viện

```bash
pip install -r requirements.txt
```

### 2. Khởi chạy ứng dụng

```bash
streamlit run app.py
```

Ứng dụng sẽ mở tại địa chỉ `http://localhost:8501` trên trình duyệt.

---

## 📌 Ghi chú

- Đặt file trọng số YOLOv8 (`.pt`) vào thư mục `data/models/`.
- Cơ sở dữ liệu SQLite sẽ được tạo tự động trong `data/db/` khi chạy lần đầu.
- Ảnh mẫu để kiểm thử có thể đặt vào `data/sample_images/`.
