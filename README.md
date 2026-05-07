# ☕ SmartCafe AI

**SmartCafe AI** là một hệ thống quản lý kho thông minh tự động dành cho các quán cà phê, ứng dụng công nghệ Trí tuệ Nhân tạo (Computer Vision) với mô hình **YOLOv8** kết hợp giao diện web tương tác được xây dựng bằng **Streamlit**.

Hệ thống cho phép tự động nhận diện và đếm số lượng các vật dụng, nguyên liệu trong quán thông qua ảnh chụp hoặc camera trực tiếp, giúp tối ưu hóa quy trình kiểm kê và quản lý kho.

---

## 🌟 Tính Năng Chính
- **AI Nhận diện Tự động**: Nhận diện 5 mặt hàng cơ bản bao gồm `Cà phê hạt`, `Cà phê xay`, `Ly giấy`, `Ly nhựa`, và `Sữa đặc`.
- **Giao diện Trực quan (Streamlit Dashboard)**: Tương tác dễ dàng với hệ thống mà không cần kiến thức lập trình phức tạp.
- **Tùy chỉnh Nhận diện Nâng cao**: Người dùng có thể tinh chỉnh ngưỡng độ nhạy (Confidence Threshold) và lựa chọn lọc từng loại mặt hàng cần nhận diện trực tiếp trên giao diện để có kết quả tốt nhất.
- **Tùy biến Kết quả (Human-in-the-loop)**: Hệ thống cho phép người dùng kiểm tra và điều chỉnh số lượng (nếu AI đếm sai) trước khi lưu vào cơ sở dữ liệu.
- **Phân tích Dữ liệu**: Hiển thị biểu đồ phân bố hàng hóa và lịch sử kiểm kho trong quá khứ.

---

## 📂 Cấu Trúc Dự Án

```
SmartCafe_AI/
│
├── smartcafe_ai/               # Thư mục chứa mã nguồn chính
│   ├── app.py                  # Điểm khởi chạy chính của ứng dụng Streamlit
│   ├── data/                   # Thư mục lưu trữ database (file CSV) và mô hình AI
│   ├── src/                    # Chứa mã nguồn cốt lõi
│   │   ├── vision.py           # Core AI sử dụng YOLOv8 xử lý hình ảnh
│   │   └── database.py         # Quản lý lưu trữ/ đọc dữ liệu kiểm kho
│   ├── ui/                     # Giao diện người dùng
│   │   ├── components.py       # Các thành phần tái sử dụng (Sidebar, Metric card)
│   │   ├── page_inventory.py   # Trang Kiểm Kho (Tải ảnh, Camera, Lịch sử)
│   │   └── page_advisor.py     # Trang AI Cố vấn (tùy chọn mở rộng)
│   └── tools/                  # Các công cụ hỗ trợ cho việc dev/test
│       ├── test_camera.py      # Test riêng biệt tính năng Camera với OpenCV
│       └── train_model.py      # Kịch bản dùng để huấn luyện mô hình YOLO
│
├── requirements.txt            # Danh sách các thư viện Python cần thiết
└── README.md                   # Tài liệu hướng dẫn sử dụng
```

---

## ⚙️ Hướng Dẫn Cài Đặt

**Bước 1:** Clone hoặc tải mã nguồn về máy tính của bạn.

**Bước 2:** Di chuyển vào thư mục dự án và cài đặt các thư viện phụ thuộc thông qua `pip`.
Nên sử dụng môi trường ảo (Virtual Environment) để tránh xung đột thư viện.

```bash
cd SmartCafe_AI
pip install -r requirements.txt
```

---

## 🚀 Hướng Dẫn Khởi Chạy Hệ Thống

Sau khi cài đặt xong môi trường, bạn có thể khởi động ứng dụng Web bằng lệnh sau (Lưu ý chạy trong thư mục `smartcafe_ai`):

```bash
cd smartcafe_ai
streamlit run app.py
```

Ứng dụng sẽ tự động mở trên trình duyệt tại địa chỉ `http://localhost:8501`.

**Lưu ý khi chạy lần đầu:** 
- Nếu bạn chưa có file mô hình YOLO (`best.pt`) được huấn luyện sẵn trong thư mục `data/models/`, hệ thống sẽ tự động dùng mô hình `yolov8n.pt` gốc (sẽ không nhận diện được chính xác các mặt hàng cụ thể của quán).
- Để AI nhận diện được cà phê, ly nhựa, v.v., bạn cần huấn luyện mô hình (thông qua `tools/train_model.py`) và thả file `best.pt` vào `smartcafe_ai/data/models/`.

---

## 🛠 Cách Thức Vận Hành Của Hệ Thống

1. **Luồng Dữ Liệu Hình Ảnh**: Người dùng tải ảnh lên hoặc chụp từ camera thông qua trang **Kiểm Kho**. Ảnh (dạng ma trận điểm ảnh RGB) sẽ được ứng dụng đẩy sang file `vision.py`.
2. **Luồng Nhận Diện (YOLOv8)**: File `vision.py` sẽ nạp mô hình AI đã học (`best.pt`). Khi nhận ảnh, YOLO sẽ quét qua để tìm các vùng chứa vật thể khớp với dữ liệu đã học. AI trả về kết quả gồm (Số lượng đếm được, và ảnh đã vẽ các khung đánh dấu vật thể). Quá trình này được lọc theo "ngưỡng độ nhạy" do người dùng cài đặt ở Sidebar.
3. **Luồng Giao Diện và Chỉnh Sửa**: Ứng dụng Streamlit hiển thị ảnh đã xử lý và số lượng lên màn hình thông qua các ô đếm `st.number_input`. Dữ liệu này được lưu tạm ở `st.session_state` giúp người dùng chỉnh sửa thủ công.
4. **Luồng Lưu Trữ**: Khi người dùng ấn nút "Lưu kho", dữ liệu từ bộ nhớ tạm sẽ được đưa vào `database.py` để lưu trữ dài hạn xuống file lịch sử CSV.
