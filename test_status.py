import os
from dotenv import load_dotenv
load_dotenv('backend/.env')
import sys
sys.path.append(os.path.join(os.getcwd(), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()
# pyrefly: ignore [missing-import]
from api.models import ConsultationModel

consultations = ConsultationModel.find_all()
print("Trying to add handled_by field...")
try:
    res = ConsultationModel.update(consultations[0]['id'], {'handled_by': 'Budi'})
    print("Success:", res)
except Exception as e:
    print("Error:", str(e))
