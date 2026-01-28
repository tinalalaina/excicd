from datetime import timedelta

from django.utils import timezone

from .models import RefreshToken


class TokenService:
    @staticmethod
    def create_refresh_token(user, token):
        expires_at = timezone.now() + timedelta(days=7)
        return RefreshToken.objects.create(
            user=user,
            token=token,
            expires_at=expires_at
        )

    @staticmethod
    def blacklist_refresh_token(token):
        rt = RefreshToken.objects.filter(token=token).first()
        if not rt:
            return False
        rt.is_blacklisted = True
        rt.save()
        return True

    @staticmethod
    def is_refresh_token_valid(token):
        rt = RefreshToken.objects.filter(token=token).first()
        if not rt:
            return False
        return rt.is_valid()
