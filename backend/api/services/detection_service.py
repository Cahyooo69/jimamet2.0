import os
from PIL import Image
import logging

logger = logging.getLogger(__name__)

class DetectionService:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    MODEL_PATH = os.path.join(BASE_DIR, 'ml_models', 'best.pt')
    model = None

    @classmethod
    def get_model(cls):
        if cls.model is None:
            if not os.path.exists(cls.MODEL_PATH):
                logger.error(f"Model file not found at {cls.MODEL_PATH}")
                return None
            try:
                from ultralytics import YOLO
                cls.model = YOLO(cls.MODEL_PATH)
                logger.info(f"YOLO model loaded successfully from {cls.MODEL_PATH}")
            except ImportError:
                logger.error("ultralytics library is not installed.")
                return None
            except Exception as e:
                logger.error(f"Error loading YOLO model: {e}")
                return None
        return cls.model

    @classmethod
    def detect_food(cls, image_file) -> list:
        model = cls.get_model()
        if not model:
            raise RuntimeError("Model deteksi makanan belum siap atau file best.pt tidak ditemukan.")
            
        try:
            from PIL import ImageOps
            # Buka gambar, perbaiki rotasi EXIF HP, dan standarisasi warna ke RGB
            raw_img = Image.open(image_file)
            img = ImageOps.exif_transpose(raw_img).convert("RGB")
            
            # Predict (matikan verbose agar log terminal lebih bersih)
            results = model(img, verbose=False)
            
            detected_foods = []
            for result in results:
                boxes = result.boxes
                for box in boxes:
                    class_id = int(box.cls[0].item())
                    confidence = float(box.conf[0].item())
                    food_name = result.names[class_id]
                    
                    # Turunkan batas keyakinan (threshold) menjadi 25% (0.25)
                    if confidence > 0.25:
                        detected_foods.append({
                            "food_name": food_name,
                            "confidence": round(confidence * 100, 2)
                        })
                        
            return detected_foods
        except Exception as e:
            logger.error(f"Error during detection: {e}")
            raise RuntimeError(f"Gagal memproses gambar: {str(e)}")
