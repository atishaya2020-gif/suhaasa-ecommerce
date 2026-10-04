from django.urls import path

from .views import CartItemsAPIView, CommerceStateAPIView, WishlistItemsAPIView

urlpatterns = [
    path("state/", CommerceStateAPIView.as_view(), name="commerce-state"),
    path("cart/items/", CartItemsAPIView.as_view(), name="cart-items"),
    path("cart/items/<int:item_id>/", CartItemsAPIView.as_view(), name="cart-item-detail"),
    path("wishlist/items/", WishlistItemsAPIView.as_view(), name="wishlist-items"),
    path("wishlist/items/<int:product_id>/", WishlistItemsAPIView.as_view(), name="wishlist-item-detail"),
]
