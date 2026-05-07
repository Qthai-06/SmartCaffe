# pyrefly: ignore [missing-import]
import cv2
# pyrefly: ignore [missing-import]
from ultralytics import YOLO
import os

def main():
    print("🚀 Đang khởi động Camera và nạp AI...")
    
    # Tìm file AI mà chúng ta vừa train
    model_path = os.path.join("models", "smartcafe", "weights", "best.pt")
    
    if os.path.exists(model_path):
        model = YOLO(model_path)
        print("✅ Đã nạp thành công bộ não Custom (SmartCafe)!")
    else:
        print("⚠️ AI vẫn đang được train (chưa sinh ra file best.pt). Dùng tạm model gốc yolov8n.pt để test camera trước...")
        model = YOLO("yolov8n.pt")

    # Mở Camera laptop
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Lỗi: Không thể mở Camera!")
        return

    print("👉 HƯỚNG DẪN:")
    print("- Đưa đồ vật vào khung hình.")
    print("- Bấm phím SPACE (Dấu cách) để CHỤP & NHẬN DIỆN.")
    print("- Bấm phím 'q' để tắt Camera.")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        # Chỉ hiển thị luồng camera bình thường (Rất nhẹ máy)
        cv2.imshow("TEST AI CAMERA - Bam SPACE de chup", frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == 32: # Mã ASCII của phím Space
            print("📸 Đang chụp và nhận diện...")
            # Hạ conf xuống cực thấp (0.15) để bắt buộc AI phải "khai" ra hết tất cả những gì nó ngờ ngợ
            results = model(frame, conf=0.15, verbose=False) 
            annotated_frame = results[0].plot()
            
            # Hiển thị ảnh đã nhận diện lên một cửa sổ mới
            cv2.imshow("KET QUA NHAN DIEN", annotated_frame)
            # Dừng lại chờ người dùng xem xong ảnh thì đóng cửa sổ kết quả
            cv2.waitKey(0) 
            try:
                cv2.destroyWindow("KET QUA NHAN DIEN")
            except:
                pass
            
    # Xóa bộ nhớ camera
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
