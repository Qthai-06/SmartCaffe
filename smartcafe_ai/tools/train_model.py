# pyrefly: ignore [missing-import]
from ultralytics import YOLO
import os
def main():
    print("🚀 BẮT ĐẦU HUẤN LUYỆN MODEL SMARTCAFE AI...")
    
    # Tải pre-trained model nhẹ nhất của YOLO11 (Nano) để làm nền tảng học
    model = YOLO("yolo11n.pt")

    # Bắt đầu train với 50 epochs (vòng lặp học). Do data ít (54 ảnh) nên chạy khoảng 5-10 phút là xong.
    results = model.train(
        data=os.path.abspath("dataset_custom/data.yaml"),
        epochs=100,       # Số vòng học (có thể tăng lên 100 nếu muốn máy thông minh hơn)
        imgsz=640,       # Kích thước ảnh chuẩn
        batch=8,         # Số lượng ảnh học trong 1 lần (tùy RAM máy)
        project=os.path.abspath("models"), # Dùng đường dẫn tuyệt đối để tránh bị lưu nhầm vào ổ C
        name="smartcafe" # Tên thư mục con
    )
    
    # --- TỰ ĐỘNG COPY MODEL ĐẾN ĐÚNG CHỖ CHO ỨNG DỤNG ---
    import shutil
    # results.save_dir sẽ chứa thư mục nơi YOLO thực tế đã lưu kết quả
    trained_weights_path = os.path.join(results.save_dir, "weights", "best.pt")
    
    # Nơi ứng dụng SmartCafe thực tế cần file best.pt (thư mục data/models)
    target_dir = os.path.abspath(os.path.join("data", "models"))
    os.makedirs(target_dir, exist_ok=True)
    target_weights_path = os.path.join(target_dir, "best.pt")
    
    # Tự động Copy file để bạn không phải làm bằng tay nữa
    if os.path.exists(trained_weights_path):
        shutil.copy(trained_weights_path, target_weights_path)
        print(f"✅ HUẤN LUYỆN XONG!")
        print(f"👉 Model đã được tự động copy và sẵn sàng sử dụng ngay tại: {target_weights_path}")
    else:
        print("❌ Có lỗi xảy ra, không tìm thấy file best.pt sau khi train.")

if __name__ == '__main__':
    main()
