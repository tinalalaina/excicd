import random
import string
from datetime import timedelta

from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone

from .models import OTPCode, User, RefreshToken
from agriculture.utils import send_email_notification


class OTPService:
    @staticmethod
    def generate_otp_code(length=None):
        length = length or getattr(settings, "OTP_LENGTH", 6)
        return "".join(random.choices(string.digits, k=length))

    # ✅ AJOUT — nettoyage des comptes non vérifiés
    @staticmethod
    def clean_unverified_users():
        """
        Supprime les utilisateurs dont l'email n'est pas vérifié
        après OTP_VALIDITY_MINUTES
        """
        limit_time = timezone.now() - timedelta(
            minutes=getattr(settings, "OTP_VALIDITY_MINUTES", 10)
        )

        User.objects.filter(
            email_verified=False,
            date_joined__lt=limit_time
        ).delete()

    @staticmethod
    def create_otp(user, purpose):
        # ✅ AJOUT — nettoyage automatique avant création OTP
        OTPService.clean_unverified_users()

        # ⬇️ CODE EXISTANT (INCHANGÉ)
        OTPCode.objects.filter(user=user, purpose=purpose, is_used=False).delete()

        code = OTPService.generate_otp_code()
        expires_at = timezone.now() + timedelta(
            minutes=getattr(settings, "OTP_VALIDITY_MINUTES", 10)
        )

        otp = OTPCode.objects.create(
            user=user,
            code=code,
            purpose=purpose,
            expires_at=expires_at,
        )
        return otp

    @staticmethod
    def verify_otp(email, code, purpose):
        user = User.objects.filter(email=email).first()
        if not user:
            return None

        otp = OTPCode.objects.filter(
            user=user,
            code=code,
            purpose=purpose,
            is_used=False,
        ).order_by("-created_at").first()

        if otp and otp.is_valid():
            otp.is_used = True
            otp.save()
            return user
        return None

    @staticmethod
    def send_otp_email(user, otp_code, purpose):
        if purpose == "email_verification":
            subject = "Vérification de votre email - agriculture"
            html_message = render_to_string(
                "otp.html",
                {
                    "OTP_CODE": otp_code,
                    "FIRST_NAME": user.first_name
                }
            )
            send_email_notification(
                html_message,
                user.email,
                subject,
                is_html=True
            )
        else:
            subject = "Réinitialisation de mot de passe - agriculture"
            html_message = render_to_string(
                "password_reset_otp.html",
                {
                    "OTP_CODE": otp_code,
                    "FIRST_NAME": user.first_name
                }
            )
            send_email_notification(
                html_message,
                user.email,
                subject,
                is_html=True
            )


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
