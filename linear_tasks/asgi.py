"""
ASGI config for Linear Tasks.

Insider is initialized before the Django application is built so
DjangoIntegration can patch the request handler.
"""

import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "linear_tasks.settings")

from linear_tasks.insider_init import init_insider  # noqa: E402

init_insider()

from django.core.asgi import get_asgi_application  # noqa: E402

application = get_asgi_application()
