import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# Plain ASGI app for now. The "Live Tracking" feature (Phase 6) needs
# WebSockets, at which point this gets wrapped with Channels'
# ProtocolTypeRouter — kept as a separate, deliberate change rather
# than pulling in channels now for a feature that isn't built yet.
application = get_asgi_application()
