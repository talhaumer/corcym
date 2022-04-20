"""corcym URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import oauth2_provider.views as oauth2_views
from django.conf.urls import include
from django.contrib import admin
from django.urls import include, path, re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

urlpatterns = [
    path("admin/", admin.site.urls),
    path("support/", include("support.urls")),
    path("news/", include("news.urls")),
    path("users/", include("users.urls")),
    path("career/", include("career.urls")),
    path("webinars/", include("webinars.urls")),
    path("contact/", include("contact.urls")),
    path("products/", include("products.urls")),
    path("o/", include("oauth2_provider.urls", namespace="oauth2_provider")),
    re_path(
        r"^oauth/authorize/$",
        oauth2_views.AuthorizationView.as_view(),
        name="authorize",
    ),
    re_path(r"^oauth/token/$", oauth2_views.TokenView.as_view(), name="token"),
    re_path(
        r"^oauth/revoke-token/$",
        oauth2_views.RevokeTokenView.as_view(),
        name="revoke-token",
    ),
]
