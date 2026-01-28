# users/views.py
from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser

from drf_spectacular.utils import extend_schema, OpenApiRequest

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView

from .models import User
from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserProfileSerializer,
    UserUpdateSerializer,
    CustomTokenRefreshSerializer,
    UserPhotoUploadSerializer,
)
from .services import TokenService


class UserRegistrationView(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(request=UserRegistrationSerializer)
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            return Response(
                {
                    "message": "Compte créé avec succès.",
                    "id": str(user.id),
                    "email": user.email,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(request=UserLoginSerializer)
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
    @extend_schema(request=OpenApiRequest(UserUpdateSerializer, media_type="multipart/form-data"))
    def patch(self, request, user_id):
        user = self.get_user(user_id)
        serializer = UserUpdateSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(UserProfileSerializer(user).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Tu peux garder PUT aussi (partial=True comme avant)
    @extend_schema(request=OpenApiRequest(UserUpdateSerializer, media_type="multipart/form-data"))
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

    @extend_schema(request=OpenApiRequest(UserPhotoUploadSerializer, media_type="multipart/form-data"))
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
