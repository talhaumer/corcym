from django.conf.urls import url
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from support.views import (
    DonationEmailSendingView,
    DonationGroupByView,
    DonationViewSet,
    EmailCityView,
    EmailCountryView,
    EmailSendingView,
    EmailViewSet,
    HowCanIHelpYouView,
    SupportGroupByView,
    WhoIAmView,
)

router = DefaultRouter()
router.register(r"donation", DonationViewSet)
router.register(r"email", EmailViewSet)
app_name = "support"

# app_name will help us do a reverse look-up latter.
urlpatterns = [
    path("email/sending", EmailSendingView.as_view(), name="email-sending"),
    path("email/sending/<int:pk>", EmailSendingView.as_view(), name="email-sending"),
    path("country", EmailCountryView.as_view(), name="support-country"),
    path("city", EmailCityView.as_view(), name="support-city"),
    path(
        "donation/email/sending",
        DonationEmailSendingView.as_view(),
        name="donation-email-sending",
    ),
    path(
        "donation/email/sending/<int:pk>",
        DonationEmailSendingView.as_view(),
        name="donation-email-sending",
    ),
    path("who-i-am", WhoIAmView.as_view(), name="who-i-am"),
    path("who-i-am/<int:pk>", WhoIAmView.as_view(), name="who-i-am"),
    path("how-can-i-help-you", HowCanIHelpYouView.as_view(), name="how-can-i-help-you"),
    path(
        "how-can-i-help-you/<int:pk>",
        HowCanIHelpYouView.as_view(),
        name="how-can-i-help-you",
    ),
    path(
        "email-support-groupby",
        SupportGroupByView.as_view(),
        name="email-support-groupby",
    ),
    path("donation-groupby", DonationGroupByView.as_view(), name="donation-groupby"),
    url(r"", include(router.urls)),
]
