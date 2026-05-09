# pyrefly: ignore [missing-import]
import os
import cv2

# pyrefly: ignore [missing-import]
from ultralytics import YOLO


class SmartCafeVision:
    def __init__(self):
        """
        Nạp model YOLO custom SmartCafe.
        Model phải nằm tại:
        D:/CNPM/AI/models/smartcafe/weights/best.pt
        """

        base_dir = os.path.dirname(os.path.abspath(__file__))

        self.model_path = os.path.join(
            base_dir,
            "models",
            "smartcafe",
            "weights",
            "best.pt"
        )

        print("MODEL PATH =", self.model_path)

        if not os.path.exists(self.model_path):
            raise FileNotFoundError(
                f"Không tìm thấy model custom tại: {self.model_path}\n"
                "Hãy kiểm tra lại file best.pt."
            )

        print("✅ Đã nạp thành công bộ não Custom SmartCafe!")
        self.model = YOLO(self.model_path)

        print("📌 Class trong model:", self.model.names)

        self.class_names = {
            0: "cafe_hat",
            1: "cafe_xay",
            2: "ly_giay",
            3: "ly_nhua",
            4: "sua_dac"
        }

    def process_frame(self, frame, conf_threshold=0.4, allowed_classes=None):
        """
        Xử lý ảnh đầu vào và trả về:
        - ảnh đã vẽ bounding box
        - số lượng từng mặt hàng
        """

        inventory_counts = {
            "cafe_hat": 0,
            "cafe_xay": 0,
            "ly_giay": 0,
            "ly_nhua": 0,
            "sua_dac": 0
        }

        if frame is None:
            return frame, inventory_counts

        class_ids = []

        if allowed_classes is not None:
            for cls_id, cls_name in self.class_names.items():
                if cls_name in allowed_classes:
                    class_ids.append(cls_id)
        else:
            class_ids = list(self.class_names.keys())

        if len(class_ids) == 0:
            return frame, inventory_counts

        results = self.model.predict(
            frame,
            conf=conf_threshold,
            imgsz=640,
            classes=class_ids,
            verbose=False
        )

        processed_frame = results[0].plot()

        for box in results[0].boxes:
            class_id = int(box.cls[0].item())

            if class_id in self.class_names:
                item_name = self.class_names[class_id]
                inventory_counts[item_name] += 1

        return processed_frame, inventory_counts


if __name__ == "__main__":
    vision = SmartCafeVision()
    print("✅ Test nạp model thành công.")