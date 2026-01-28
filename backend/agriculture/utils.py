import logging
import os
from urllib.parse import urlparse

from django.conf import settings
from django.core.files.storage import default_storage
from django.core.mail import EmailMessage

logger = logging.getLogger(__name__)

class Util:
    @staticmethod
    def send_email(data):
        email = EmailMessage(
            subject=data["email_subject"],
            body=data["email_body"],
            to=[data["to_email"]],
        )
        email.content_subtype = "html"
        email.send()


def send_email_notification(email_content, email, titre, is_html=True):
    content = {
        "email_body": email_content,
        "to_email": email,
        "email_subject": titre,
        "is_html": is_html,
    }
    Util.send_email(content)


def _normalize_media_path(path_or_url: str):
    if not path_or_url:
        return None

    path_or_url = str(path_or_url)
    parsed = urlparse(path_or_url)

    if parsed.scheme and parsed.netloc:
        candidate = parsed.path
    else:
        candidate = path_or_url

    if settings.MEDIA_URL and candidate.startswith(settings.MEDIA_URL):
        candidate = candidate.replace(settings.MEDIA_URL, "", 1)

    candidate = candidate.lstrip("/")
    return candidate or None


def delete_file(path_or_url: str):
    relative_path = _normalize_media_path(path_or_url)
    if not relative_path:
        return

    try:
        if default_storage.exists(relative_path):
            default_storage.delete(relative_path)
            return

        absolute_path = os.path.join(settings.MEDIA_ROOT, relative_path)
        if os.path.exists(absolute_path):
            os.remove(absolute_path)

    except Exception as exc:
        logger.warning("Impossible de supprimer le fichier %s : %s", relative_path, exc)
