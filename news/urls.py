from django.conf.urls import url
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from news.views import (
    DeletedNewsView,
    DeleteNewsView,
    NewsReleaseView,
    NewsView,
    NewsViewSet,
    PressReleaseView,
    TopNewsView,
)

router = DefaultRouter()
router.register(r"news", NewsViewSet)

app_name = "news"

# app_name will help us do a reverse look-up latter.
urlpatterns = [
    path("news", NewsView.as_view(), name="news"),
    path("news/<int:pk>", NewsView.as_view(), name="news"),
    path("deleted-news/<int:pk>", DeletedNewsView.as_view(), name="deleted-news"),
    path("top/news/", TopNewsView.as_view(), name="top-news"),
    path("news/<int:pk>", TopNewsView.as_view(), name="top-news"),
    path("press/news/", PressReleaseView.as_view(), name="press-relaese"),
    path("press/news/<int:pk>", PressReleaseView.as_view(), name="press-relaese"),
    path("news/listing/", NewsReleaseView.as_view(), name="press-news"),
    path("news/listing/<int:pk>", NewsReleaseView.as_view(), name="press-news"),
    url(r"api/", include(router.urls)),
    path("delete/news/<int:pk>", DeleteNewsView.as_view(), name="delete-news"),
]
