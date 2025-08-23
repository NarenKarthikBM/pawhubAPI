from django.urls import path

from . import views

urlpatterns = [
    path(
        "obtain-auth-token/",
        views.UserObtainAuthTokenAPI.as_view(),
        name="user-obtain-auth-token",
    ),
    path(
        "register/",
        views.UserRegistrationAPI.as_view(),
        name="user-registration",
    ),
]
