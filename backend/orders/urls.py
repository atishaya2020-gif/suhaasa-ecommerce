from django.urls import path

from .views import CancelPendingOrderAPIView, CreateOrderAPIView, OrderDetailAPIView, OrderListAPIView, ReorderAPIView

urlpatterns = [
    path("", OrderListAPIView.as_view(), name="order-list"),
    path("create/", CreateOrderAPIView.as_view(), name="order-create"),
    path("<str:order_number>/cancel/", CancelPendingOrderAPIView.as_view(), name="order-cancel"),
    path("<str:order_number>/reorder/", ReorderAPIView.as_view(), name="order-reorder"),
    path("<str:order_number>/", OrderDetailAPIView.as_view(), name="order-detail"),
]
