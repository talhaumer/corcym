from django.urls import path, include
from django.conf.urls import url

from contact.views import ContactViewSet,ContactView, IWouldView, SpecialtyView, InterestInView
from rest_framework.routers import DefaultRouter
from django.conf.urls import url



router = DefaultRouter()
router.register(r'contact', ContactViewSet)



app_name = "contact"

# app_name will help us do a reverse look-up latter.
urlpatterns = [

    path('contact', ContactView.as_view(), name='contact'),
    path('contact/<int:pk>', ContactView.as_view(), name='contact'),

    path('i-would', IWouldView.as_view(), name='i-would'),

    path('specialty', SpecialtyView.as_view(), name='specialty'),

    path('intrest', InterestInView.as_view(), name='intrest'),

    url(r'', include(router.urls)),

    ]