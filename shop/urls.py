from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("catalog/", views.catalog, name="catalog"),
    path("product/<int:id>/", views.product, name="product"),
    path("add/<int:id>/", views.add_to_cart, name="add_to_cart"),
    path("cart/", views.cart, name="cart"),
    path("increase/<int:index>/", views.increase_qty, name="increase"),
    path("decrease/<int:index>/", views.decrease_qty, name="decrease"),
    path("remove/<int:index>/", views.remove_from_cart, name="remove_from_cart"),
    path("checkout/", views.checkout, name="checkout"),
    path("success/", views.success, name="success"),
    path("about/", views.about, name="about"),
    path("register/", views.register, name="register"),
    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),
]