# pyrefly: ignore [missing-import]
import ast
import logging
import os
from typing import Dict, List, Optional, Tuple

import cv2
# pyrefly: ignore [missing-import]
from ultralytics import YOLO

DEFAULT_CLASSES = ["cafe_hat", "cafe_xay", "ly_giay", "ly_nhua", "sua_dac"]
ALIASES = {"lygiay": "ly_giay", "ly_giay": "ly_giay", "ly-giay": "ly_giay", "Ly_giay": "ly_giay"}
logger = logging.getLogger(__name__)


def _normalize_class_name(name: str) -> str:
    raw = str(name or "").strip()
    lowered = raw.lower()
    lowered = lowered.replace(" ", "_")
    return ALIASES.get(lowered, lowered)


def _load_expected_classes(base_dir: str) -> List[str]:
    env_classes = os.getenv("SMARTCAFE_CLASSES", "").strip()
    if env_classes:
        classes = [_normalize_class_name(x) for x in env_classes.split(",") if x.strip()]
        dedup = []
        for c in classes:
            if c not in dedup:
                dedup.append(c)
        return dedup or DEFAULT_CLASSES

    data_yaml = os.path.join(os.path.dirname(base_dir), "dataset_custom", "data.yaml")
    if not os.path.exists(data_yaml):
        return DEFAULT_CLASSES

    try:
        with open(data_yaml, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip().startswith("names:"):
                    raw_names = line.split(":", 1)[1].strip()
                    parsed = ast.literal_eval(raw_names)
                    if isinstance(parsed, list):
                        classes = [_normalize_class_name(x) for x in parsed]
                        dedup = []
                        for c in classes:
                            if c and c not in dedup:
                                dedup.append(c)
                        if dedup:
                            return dedup
    except (OSError, ValueError, SyntaxError) as ex:
        logger.warning("Cannot parse dataset class names from %s: %s", data_yaml, ex)
        return DEFAULT_CLASSES

    return DEFAULT_CLASSES


def _model_path_candidates(base_dir: str) -> List[str]:
    project_root = os.path.dirname(os.path.dirname(base_dir))
    env_path = os.getenv("SMARTCAFE_MODEL_PATH", "").strip()
    candidates = [env_path] if env_path else []
    candidates.extend(
        [
            os.path.join(os.path.dirname(base_dir), "data", "models", "best.pt"),
            os.path.join(os.path.dirname(base_dir), "models", "smartcafe", "weights", "best.pt"),
            os.path.join(os.path.dirname(base_dir), "models", "best.pt"),
            os.path.join(project_root, "yolov8n.pt"),
        ]
    )
    return [p for p in candidates if p]


class SmartCafeVision:
    def __init__(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        candidates = _model_path_candidates(base_dir)
        self.model_path: Optional[str] = None

        for p in candidates:
            if os.path.exists(p):
                self.model_path = p
                break

        if not self.model_path:
            raise FileNotFoundError(
                "Không tìm thấy model AI. Thiết lập SMARTCAFE_MODEL_PATH hoặc đặt best.pt tại smartcafe_ai/data/models/."
            )

        self.model = YOLO(self.model_path)
        self.expected_classes = _load_expected_classes(base_dir)
        self.class_names = self._build_class_mapping()

        if not self.class_names:
            raise ValueError(
                "Model không có class trùng với cấu hình SmartCafe. "
                "Hãy kiểm tra SMARTCAFE_CLASSES hoặc dataset_custom/data.yaml."
            )

    def _build_class_mapping(self) -> Dict[int, str]:
        raw_model_names = self.model.names
        mapping: Dict[int, str] = {}

        if isinstance(raw_model_names, dict):
            iterator = raw_model_names.items()
        else:
            iterator = enumerate(raw_model_names)

        expected = set(self.expected_classes)
        for idx, name in iterator:
            normalized = _normalize_class_name(str(name))
            if normalized in expected:
                mapping[int(idx)] = normalized

        return mapping

    def process_frame(
        self, frame, conf_threshold: float = 0.4, allowed_classes: Optional[List[str]] = None
    ) -> Tuple[object, Dict[str, int]]:
        inventory_counts = {item: 0 for item in DEFAULT_CLASSES}
        if frame is None:
            return frame, inventory_counts

        allowed_set = set(_normalize_class_name(x) for x in (allowed_classes or DEFAULT_CLASSES))
        class_ids = [idx for idx, name in self.class_names.items() if name in allowed_set]
        if not class_ids:
            return frame, inventory_counts

        results = self.model.predict(
            frame,
            conf=conf_threshold,
            imgsz=640,
            classes=class_ids,
            verbose=False,
        )

        processed_frame = results[0].plot()
        for box in results[0].boxes:
            class_id = int(box.cls[0].item())
            item_name = self.class_names.get(class_id)
            if item_name:
                inventory_counts[item_name] += 1

        if len(frame.shape) == 2:
            processed_frame = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2GRAY)
        return processed_frame, inventory_counts


if __name__ == "__main__":
    SmartCafeVision()
    print("✅ Test nạp model thành công.")
