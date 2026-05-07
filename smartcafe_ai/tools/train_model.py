# pyrefly: ignore [missing-import]
from ultralytics import YOLO
import os
def main():
    print("🚀 BẮT ĐẦU HUẤN LUYỆN MODEL SMARTCAFE AI...")
    
    # Tải pre-trained model nhẹ nhất của YOLO (Nano) để làm nền tảng học
    model = YOLO("yolov8n.pt") 

    # Bắt đầu train với 50 epochs (vòng lặp học). Do data ít (54 ảnh) nên chạy khoảng 5-10 phút là xong.
    results = model.train(
        data=os.path.abspath("dataset_custom/data.yaml"),
        epochs=50,       # Số vòng học (có thể tăng lên 100 nếu muốn máy thông minh hơn)
        imgsz=640,       # Kích thước ảnh chuẩn
        batch=8,         # Số lượng ảnh học trong 1 lần (tùy RAM máy)
        project="models",# Thư mục lưu kết quả
        name="smartcafe" # Tên thư mục con
    )
    
    print("✅ HUẤN LUYỆN XONG! Trọng số model được lưu tại: models/smartcafe/weights/best.pt")

if __name__ == '__main__':
    main()
