"""
WSGI config for agriculture project.
"""

import os
from django.core.wsgi import get_wsgi_application

from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "agriculture.settings")

application = get_wsgi_application()
application = WhiteNoise(application, root=settings.STATIC_ROOT)

