# users/serializers.py
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import authenticate, get_user_model

from rest_framework_simplejwt.serializers import TokenRefreshSerializer

from .models import User, OTPCode, RefreshToken
from agriculture.utils import delete_file


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            "email",
            "password",
            "password_confirm",
            "first_name",
            "last_name",
            "phone",
            "role",
        )
        extra_kwargs = {
            "email": {"required": True},
            "first_name": {"required": True},
            "last_name": {"required": True},
        }

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError(
                {"password_confirm": "Les mots de passe ne correspondent pas."}
            )
        return attrs

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        password = validated_data.pop("password")

        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.email_verified = False
        user.is_active = False
        user.save()
        return user


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        if email and password:
            user = authenticate(username=email, password=password)
            if not user:
                raise serializers.ValidationError("verifier votre email ou mot de passe.")
            if not user.is_active:
                raise serializers.ValidationError("Compte est désactivé.")
            if not user.email_verified:
                raise serializers.ValidationError(
                    "Veuillez vérifier votre email avant de vous connecter."
                )

            attrs["user"] = user
            return attrs

        raise serializers.ValidationError("Email et mot de passe requis.")


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "phone",
            "profession",
            "residence",
            "cin_number",
            "address",
            "date_of_birth",
            "image",
            "cin_photo_recto",
            "cin_photo_verso",
        )

    def update(self, instance, validated_data):
        new_photo = validated_data.get("image", None)
        if new_photo and instance.image and new_photo != instance.image:
            delete_file(instance.image.path)

        if "cin_photo_recto" in validated_data and instance.cin_photo_recto:
            delete_file(instance.cin_photo_recto.path)

        if "cin_photo_verso" in validated_data and instance.cin_photo_verso:
            delete_file(instance.cin_photo_verso.path)

        return super().update(instance, validated_data)


class OTPRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()
    purpose = serializers.ChoiceField(choices=["email_verification", "password_reset"])


class OTPVerifySerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=10)
    purpose = serializers.ChoiceField(choices=["email_verification", "password_reset"])


class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        try:
            return super().validate(attrs)
        except get_user_model().DoesNotExist:
            raise AuthenticationFailed(
                "Utilisateur introuvable ou supprimé.", code="user_not_found"
            )


class UserPhotoUploadSerializer(serializers.Serializer):
    photo = serializers.ImageField()

    def update(self, instance, validated_data):
        if instance.image:
            delete_file(instance.image.path)
        instance.image = validated_data["photo"]
        instance.save()
        return instance

    def validate_photo(self, value):
        max_size = 3 * 1024 * 1024
        if value.size > max_size:
            raise serializers.ValidationError("L'image ne doit pas dépasser 3MB.")
        valid_types = ["image/jpeg", "image/png", "image/jpg"]
        if value.content_type not in valid_types:
            raise serializers.ValidationError("Formats acceptés : JPG, PNG.")
        return value


class PasswordResetWithOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)
    new_password = serializers.CharField(min_length=8)
    new_password_confirm = serializers.CharField(min_length=8)

    def validate(self, attrs):
        if attrs["new_password"] != attrs["new_password_confirm"]:
            raise serializers.ValidationError(
                {"new_password_confirm": "Les mots de passe ne correspondent pas."}
            )
        return attrs
