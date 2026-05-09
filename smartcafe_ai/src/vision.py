# pyrefly: ignore [missing-import]
import cv2
import os
# pyrefly: ignore [missing-import]
from ultralytics import YOLO

class SmartCafeVision:
    def __init__(self):
        """
        Khởi tạo model YOLO custom đã được huấn luyện.
        """
        # Đường dẫn tới model tốt nhất sau khi train
        # Cập nhật đường dẫn cho phù hợp với cấu trúc của SmartCafe_AI
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        model_path = os.path.join(base_dir, "data", "models", "best.pt")
        
        # Nếu chưa train xong thì tạm dùng model rỗng
        if not os.path.exists(model_path):
            print(f"⚠️ Chưa tìm thấy {model_path}. Tạm dùng yolo11n.pt...")
            self.model = YOLO("yolo11n.pt")
        else:
            print("✅ Đã nạp thành công bộ não Custom SmartCafe!")
            self.model = YOLO(model_path)
            
        # Dictionary chứa tên các nhãn để dễ hiển thị
        self.class_names = {
            0: 'cafe_hat',
            1: 'cafe_xay',
            2: 'ly_giay',
            3: 'ly_nhua',
            4: 'sua_dac'
        }
        
    def process_frame(self, frame, conf_threshold=0.2, allowed_classes=None):
        """
        Xử lý frame ảnh, nhận diện 5 mặt hàng của quán.
        
        Args:
            frame: Ảnh đầu vào từ camera (numpy array dạng BGR).
            conf_threshold: Độ nhạy của AI (0.0 đến 1.0)
            allowed_classes: Danh sách các tên mặt hàng cho phép nhận diện
            
        Returns:
            processed_frame: Ảnh đã vẽ bounding box.
            inventory_counts: Dictionary chứa số lượng của 5 mặt hàng.
        """
        # Khởi tạo bộ đếm
        inventory_counts = {
            'cafe_hat': 0, 'cafe_xay': 0, 'ly_giay': 0, 'ly_nhua': 0, 'sua_dac': 0
        }

        # Lọc ID của các class được phép nhận diện
        class_ids = []
        if allowed_classes is not None:
            for cls_id, cls_name in self.class_names.items():
                if cls_name in allowed_classes:
                    class_ids.append(cls_id)
        else:
            class_ids = list(self.class_names.keys())

        # Thực hiện dự đoán chỉ khi có ít nhất 1 class được chọn
        if len(class_ids) > 0:
            results = self.model(frame, conf=conf_threshold, classes=class_ids, verbose=False)
            
            # Vẽ bounding box lên ảnh
            processed_frame = results[0].plot()
            
            # Cập nhật số lượng
            for box in results[0].boxes:
                class_id = int(box.cls[0].item())
                if class_id in self.class_names:
                    item_name = self.class_names[class_id]
                    inventory_counts[item_name] += 1
        else:
            # Nếu người dùng bỏ chọn tất cả, trả về ảnh gốc
            processed_frame = frame
                
        return processed_frame, inventory_counts
