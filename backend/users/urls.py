# users/urls.py
from django.urls import path
from users import views

urlpatterns = [
    # Auth
    path("register/", views.UserRegistrationView.as_view(), name="register"),
    path("login/", views.UserLoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("token/refresh/", views.CustomTokenRefreshView.as_view(), name="token_refresh"),

    # Profile
    path("profile/<uuid:user_id>/", views.UserProfileView.as_view(), name="profile"),
    path("profile/<uuid:user_id>/photo/", views.UserProfilePhotoView.as_view(), name="profile-photo"),

    # user info by token
    path("user-info/", views.UserInfoView.as_view(), name="user_info"),

]
