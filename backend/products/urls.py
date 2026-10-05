from django.urls import path
from .views import (
    CategoryListAPIView,
    InventoryAdjustmentAPIView,
    InventoryAdjustmentListAPIView,
    InventoryDashboardAPIView,
    InventoryVariantListAPIView,
    ProductDetailAPIView,
    ProductListAPIView,
)

urlpatterns = [
    path("categories/", CategoryListAPIView.as_view(), name="category-list"),
    path("inventory/dashboard/", InventoryDashboardAPIView.as_view(), name="inventory-dashboard"),
    path("inventory/variants/", InventoryVariantListAPIView.as_view(), name="inventory-variant-list"),
    path("inventory/adjustments/", InventoryAdjustmentAPIView.as_view(), name="inventory-adjustment-create"),
    path("inventory/history/", InventoryAdjustmentListAPIView.as_view(), name="inventory-history"),
    path("", ProductListAPIView.as_view(), name="product-list"),
    path("<slug:slug>/", ProductDetailAPIView.as_view(), name="product-detail"),
]
