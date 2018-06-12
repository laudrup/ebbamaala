"""
WSGI config for ebbamåla project.
"""
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ebbamåla.settings')
os.environ.setdefault('DJANGO_CONFIGURATION', 'Development')

from configurations.wsgi import get_wsgi_application

application = get_wsgi_application()
