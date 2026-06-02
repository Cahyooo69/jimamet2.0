import logging
from django.http import JsonResponse
from api.services.detection_service import DetectionService

from django.views.decorators.csrf import csrf_exempt

logger = logging.getLogger(__name__)

@csrf_exempt
def detect_food_api(request):
    """
    Endpoint untuk mengunggah gambar dan mendeteksi makanan menggunakan YOLOv8.
    """
    if request.method == "POST":
        if "image" not in request.FILES:
            return JsonResponse({"status": "error", "message": "Tidak ada gambar yang diunggah"}, status=400)
            
        image_file = request.FILES["image"]
        
        try:
            # Panggil layanan deteksi
            predictions = DetectionService.detect_food(image_file)
            
            return JsonResponse({
                "status": "success",
                "message": "Deteksi berhasil",
                "data": predictions
            }, status=200)
        except Exception as e:
            logger.error(f"Detection API error: {str(e)}")
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
            
    return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)
