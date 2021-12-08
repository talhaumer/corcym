from django.urls import path, include
from django.conf.urls import url

from products.views import AddProductView, ProductsGetView, BiologicalProductsGetView, MechanicalProductsGetView
app_name = "products"

# app_name will help us do a reverse look-up latter.
urlpatterns = [

    path('add-products', AddProductView.as_view(), name='add-products'),
    path('products-listing', ProductsGetView.as_view(), name='products-listing'),

    path('biological-products', BiologicalProductsGetView.as_view(), name= "biological-products"),

    path('mechanical-products', MechanicalProductsGetView.as_view(), name = "future-webinar"),

    # path('past-webinar', PastWebinarView.as_view(), name = "past-webinar")
    ]