from django.urls import include, path

from users.views import (
    AuthUserLoginView,
    LoginOperatorView,
    OperatorResgistarationView,
    UpdateProfileView,
)

urlpatterns = [
    path("login/", AuthUserLoginView.as_view(), name="user-login"),
    path(
        "operator/signup", OperatorResgistarationView.as_view(), name="operator-signup"
    ),
    path("login/operator", LoginOperatorView.as_view(), name="operator-login"),
    path("update/profile/<int:pk>", UpdateProfileView.as_view(), name="update-profile"),
]
