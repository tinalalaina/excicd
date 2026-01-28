# users/models.py
import uuid
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("L'email est obligatoire")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("email_verified", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Le superuser doit avoir is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Le superuser doit avoir is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ("CLIENT", "Client"),
        ("PRESTATAIRE", "Prestataire"),
        ("ADMIN", "Administrateur"),
        ("SUPPORT", "Support"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)

    phone = models.CharField(max_length=20, blank=True, null=True)

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="CLIENT")
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)

    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)

    # ✅ Ajouts demandés
    profession = models.CharField(max_length=120, blank=True)
    residence = models.CharField(max_length=120, blank=True)

    cin_number = models.CharField(max_length=50, blank=True, null=True)
    cin_photo_recto = models.ImageField(
        upload_to="cin/photos/recto/", blank=True, null=True
    )
    cin_photo_verso = models.ImageField(
        upload_to="cin/photos/verso/", blank=True, null=True
    )

    image = models.ImageField(upload_to="profile/photos/", blank=True, null=True)

    address = models.TextField(blank=True)
    date_of_birth = models.DateField(null=True, blank=True)

    date_joined = models.DateTimeField(default=timezone.now)

    # ✅ Important: AbstractBaseUser gère déjà last_login → ne pas redéfinir ici
    # last_login = models.DateTimeField(null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=True)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        db_table = "users"

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()


class RefreshToken(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="refresh_tokens")
    token = models.CharField(max_length=500, unique=True)
    expires_at = models.DateTimeField()
    is_blacklisted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "refresh_tokens"
        indexes = [
            models.Index(fields=["user", "is_blacklisted"]),
        ]

    def is_valid(self):
        return (not self.is_blacklisted) and (timezone.now() < self.expires_at)
