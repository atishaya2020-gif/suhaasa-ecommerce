from django.urls import path

from .views import AddressDetailAPIView, AddressListCreateAPIView, LoginAPIView, MeAPIView, RegisterAPIView

urlpatterns = [
    path("register/", RegisterAPIView.as_view(), name="register"),
    path("login/", LoginAPIView.as_view(), name="login"),
    path("me/", MeAPIView.as_view(), name="me"),
    path("addresses/", AddressListCreateAPIView.as_view(), name="address-list-create"),
    path("addresses/<int:pk>/", AddressDetailAPIView.as_view(), name="address-detail"),
]
