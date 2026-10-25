import os
import sys
from pathlib import Path

backend_path = Path(__file__).resolve().parent / 'backend'
sys.path.insert(0, str(backend_path))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()