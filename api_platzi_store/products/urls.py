from django.urls import path
from . import views

app_name = "products"

urlpatterns = [
    path("", views.home, name="home"),  # ← nuevo home
    path("productos/", views.product_list, name="product_list"),
    path("crear/", views.product_create, name="product_create"),
    path("actualizar/<int:product_id>/", views.product_update, name="product_update"),
    path("eliminar/<int:product_id>/", views.product_delete, name="product_delete"),
]
