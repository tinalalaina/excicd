# users/views.py
from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView

from .models import User
from .serializers import (
    UserRegistrationSerializer,
    UserProfileSerializer,
    UserUpdateSerializer,
    OTPRequestSerializer,
    OTPVerifySerializer,
    CustomTokenRefreshSerializer,
    UserPhotoUploadSerializer,
    PasswordResetWithOTPSerializer,
)
from .services import OTPService, TokenService


# ✅ Swagger: support multipart/form-data for profile (text + files)
profile_form_params = [
    openapi.Parameter("first_name", openapi.IN_FORM, type=openapi.TYPE_STRING, required=False),
    openapi.Parameter("last_name", openapi.IN_FORM, type=openapi.TYPE_STRING, required=False),
    openapi.Parameter("phone", openapi.IN_FORM, type=openapi.TYPE_STRING, required=False),
    openapi.Parameter("profession", openapi.IN_FORM, type=openapi.TYPE_STRING, required=False),
    openapi.Parameter("residence", openapi.IN_FORM, type=openapi.TYPE_STRING, required=False),
    openapi.Parameter("cin_number", openapi.IN_FORM, type=openapi.TYPE_STRING, required=False),
    openapi.Parameter("address", openapi.IN_FORM, type=openapi.TYPE_STRING, required=False),
    openapi.Parameter(
        "date_of_birth",
        openapi.IN_FORM,
        type=openapi.TYPE_STRING,
        required=False,
        description="YYYY-MM-DD",
    ),
    openapi.Parameter("image", openapi.IN_FORM, type=openapi.TYPE_FILE, required=False),
    openapi.Parameter("cin_photo_recto", openapi.IN_FORM, type=openapi.TYPE_FILE, required=False),
    openapi.Parameter("cin_photo_verso", openapi.IN_FORM, type=openapi.TYPE_FILE, required=False),
]


class UserRegistrationView(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(request_body=UserRegistrationSerializer)
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            otp = OTPService.create_otp(user, "email_verification")
            OTPService.send_otp_email(user, otp.code, "email_verification")

            return Response(
                {
                    "message": "Compte créé. Un code OTP a été envoyé à votre email.",
                    "id": str(user.id),
                    "email": user.email,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["email", "password"],
            properties={
                "email": openapi.Schema(type=openapi.TYPE_STRING),
                "password": openapi.Schema(type=openapi.TYPE_STRING),
            },
        )
    )
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response({"detail": "Email et mot de passe requis."}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(email=email).first()
        if not user or not user.check_password(password):
            return Response({"detail": "verifier votre email ou mot de passe."}, status=status.HTTP_401_UNAUTHORIZED)

        if not user.is_active:
            return Response({"detail": "Compte inactif."}, status=status.HTTP_403_FORBIDDEN)

        if not user.email_verified:
            return Response({"detail": "Veuillez vérifier votre email avant de vous connecter."}, status=status.HTTP_400_BAD_REQUEST)

        # ✅ last_login (JWT login ne le met pas à jour automatiquement)
        user.last_login = timezone.now()
        user.save(update_fields=["last_login"])

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        # (optionnel) store refresh token in DB (si tu veux gérer blacklist)
        TokenService.create_refresh_token(user, refresh_token)

        return Response(
            {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user": UserProfileSerializer(user).data,
            },
            status=status.HTTP_200_OK,
        )


class OTPRequestView(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(request_body=OTPRequestSerializer)
    def post(self, request):
        serializer = OTPRequestSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            purpose = serializer.validated_data["purpose"]

            user = User.objects.filter(email=email).first()
            if not user:
                return Response({"error": "Aucun utilisateur avec cet email."}, status=status.HTTP_404_NOT_FOUND)

            otp = OTPService.create_otp(user, purpose)
            OTPService.send_otp_email(user, otp.code, purpose)

            return Response({"message": f"Code {purpose} envoyé avec succès."}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OTPVerifyView(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(request_body=OTPVerifySerializer)
    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            code = serializer.validated_data["code"]
            purpose = serializer.validated_data["purpose"]

            user = OTPService.verify_otp(email, code, purpose)
            if not user:
                return Response(
                    {"error": "Code invalide ou expiré.", "verified": False},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            response_data = {"message": "Vérification réussie.", "verified": True}

            if purpose == "email_verification":
                user.email_verified = True
                user.is_active = True
                user.last_login = timezone.now()
                user.save(update_fields=["email_verified", "is_active", "last_login"])

                refresh = RefreshToken.for_user(user)
                response_data.update(
                    {
                        "access_token": str(refresh.access_token),
                        "refresh_token": str(refresh),
                        "user_id": str(user.id),
                        "email": user.email,
                        "role": user.role,
                    }
                )

                TokenService.create_refresh_token(user, response_data["refresh_token"])

            return Response(response_data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomTokenRefreshView(TokenRefreshView):
    serializer_class = CustomTokenRefreshSerializer


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh_token")
        if refresh_token:
            TokenService.blacklist_refresh_token(refresh_token)
        return Response({"message": "Déconnexion réussie."}, status=status.HTTP_200_OK)


class UserProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_user(self, user_id):
        return get_object_or_404(User, id=user_id)

    def get(self, request, user_id):
        user = self.get_user(user_id)
        return Response(UserProfileSerializer(user).data, status=status.HTTP_200_OK)

    # ✅ PATCH ajouté (partial update) + swagger multipart (cin recto/verso + image)
    @swagger_auto_schema(manual_parameters=profile_form_params, consumes=["multipart/form-data"])
    def patch(self, request, user_id):
        user = self.get_user(user_id)
        serializer = UserUpdateSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(UserProfileSerializer(user).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Tu peux garder PUT aussi (partial=True comme avant)
    @swagger_auto_schema(manual_parameters=profile_form_params, consumes=["multipart/form-data"])
    def put(self, request, user_id):
        user = self.get_user(user_id)
        serializer = UserUpdateSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(UserProfileSerializer(user).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserInfoView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(UserProfileSerializer(request.user).data, status=status.HTTP_200_OK)


class UserProfilePhotoView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    @swagger_auto_schema(request_body=UserPhotoUploadSerializer, consumes=["multipart/form-data"])
    def post(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        serializer = UserPhotoUploadSerializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {
                "message": "Photo mise à jour avec succès",
                "photo_url": user.image.url if user.image else None,
            },
            status=status.HTTP_200_OK,
        )


class PasswordResetWithOTPView(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_description="Réinitialisation du mot de passe avec OTP",
        request_body=PasswordResetWithOTPSerializer,
        responses={
            200: openapi.Response("Mot de passe réinitialisé avec succès"),
            400: "OTP invalide ou expiré",
        },
    )
    def post(self, request):
        serializer = PasswordResetWithOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        code = serializer.validated_data["code"]
        new_password = serializer.validated_data["new_password"]

        user = OTPService.verify_otp(email, code, "password_reset")

        if not user:
            return Response({"error": "Code invalide ou expiré"}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()

        return Response({"message": "Mot de passe réinitialisé avec succès"}, status=status.HTTP_200_OK)
