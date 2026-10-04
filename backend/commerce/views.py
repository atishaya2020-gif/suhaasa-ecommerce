import uuid

from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from products.models import Product, ProductVariant

from .models import CartItem, GuestSession, WishlistItem
from .serializers import CartItemSerializer, WishlistItemSerializer

TOKEN_HEADER = "HTTP_X_SUHAASA_GUEST_TOKEN"


def get_guest_session(request, create=True):
    if getattr(request, "user", None) is not None and request.user.is_authenticated:
        session = GuestSession.objects.filter(user=request.user).first()
        if session:
            return session
        if create:
            return GuestSession.objects.create(user=request.user)
        return None
    raw_token = request.META.get(TOKEN_HEADER, "").strip()
    try:
        token = uuid.UUID(raw_token)
    except (ValueError, AttributeError):
        token = None

    if token:
        session = GuestSession.objects.filter(token=token).first()
        if session:
            return session

    if not create:
        return None
    return GuestSession.objects.create()


def merge_guest_into_user(user, guest_token=None):
    user_session = GuestSession.objects.filter(user=user).first()
    guest_session = None
    if guest_token:
        try:
            guest_session = GuestSession.objects.filter(token=uuid.UUID(guest_token), user__isnull=True).first()
        except (ValueError, AttributeError):
            guest_session = None

    if not user_session:
        if guest_session:
            guest_session.user = user
            guest_session.save(update_fields=["user", "updated_at"])
            from orders.models import Order
            Order.objects.filter(session=guest_session, user__isnull=True).update(user=user)
            return guest_session
        return GuestSession.objects.create(user=user)

    if guest_session and guest_session.pk != user_session.pk:
        with transaction.atomic():
            from orders.models import Order
            Order.objects.filter(session=guest_session, user__isnull=True).update(user=user, session=user_session)
            for guest_item in guest_session.cart_items.select_related("variant"):
                item = user_session.cart_items.filter(variant=guest_item.variant).first()
                if item:
                    item.quantity = min(item.quantity + guest_item.quantity, guest_item.variant.stock_quantity)
                    item.save(update_fields=["quantity", "updated_at"])
                elif guest_item.quantity <= guest_item.variant.stock_quantity:
                    guest_item.pk = None
                    guest_item.session = user_session
                    guest_item.save()
            for guest_item in guest_session.wishlist_items.all():
                WishlistItem.objects.get_or_create(session=user_session, product=guest_item.product)
            guest_session.delete()
    return user_session


def session_payload(session):
    cart_items = session.cart_items.select_related("variant__product").prefetch_related("variant__product__images")
    wishlist_items = session.wishlist_items.select_related("product", "product__category").prefetch_related("product__images", "product__variants")
    cart_data = CartItemSerializer(cart_items, many=True).data
    wishlist_data = WishlistItemSerializer(wishlist_items, many=True).data
    subtotal = sum(item["line_total"] for item in cart_data)
    quantity = sum(item["quantity"] for item in cart_data)
    return {
        "token": str(session.token),
        "cart": cart_data,
        "cart_count": quantity,
        "subtotal": subtotal,
        "wishlist": wishlist_data,
        "wishlist_product_ids": [item["product"]["id"] for item in wishlist_data],
    }


class CommerceStateAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        session = get_guest_session(request)
        return Response(session_payload(session))


class CartItemsAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        session = get_guest_session(request)
        variant_id = request.data.get("variant_id")
        quantity = request.data.get("quantity", 1)
        try:
            variant_id = int(variant_id)
            quantity = int(quantity)
        except (TypeError, ValueError):
            return Response({"detail": "variant_id and quantity must be integers."}, status=status.HTTP_400_BAD_REQUEST)
        if quantity < 1:
            return Response({"detail": "quantity must be at least 1."}, status=status.HTTP_400_BAD_REQUEST)

        variant = get_object_or_404(ProductVariant.objects.select_related("product"), pk=variant_id, is_active=True, product__is_active=True)
        with transaction.atomic():
            item, created = CartItem.objects.select_for_update().get_or_create(session=session, variant=variant)
            # Add-to-bag is an explicit user action. If the exact same request is
            # retried while the previous request is still being processed, the
            # frontend lock prevents a duplicate submission. Once an item exists,
            # subsequent intentional Add-to-bag actions add the selected quantity.
            new_quantity = quantity if created else item.quantity + quantity
            if new_quantity > variant.stock_quantity:
                return Response({"detail": f"Only {variant.stock_quantity} units are available for {variant.name}."}, status=status.HTTP_409_CONFLICT)
            item.quantity = new_quantity
            item.save(update_fields=["quantity", "updated_at"])
        return Response(session_payload(session), status=status.HTTP_200_OK)

    def patch(self, request, item_id):
        session = get_guest_session(request, create=False)
        if not session:
            return Response({"detail": "Cart session not found."}, status=status.HTTP_404_NOT_FOUND)
        item = get_object_or_404(CartItem.objects.select_related("variant"), pk=item_id, session=session)
        try:
            quantity = int(request.data.get("quantity"))
        except (TypeError, ValueError):
            return Response({"detail": "quantity must be an integer."}, status=status.HTTP_400_BAD_REQUEST)
        if quantity < 1:
            item.delete()
        elif quantity > item.variant.stock_quantity:
            return Response({"detail": f"Only {item.variant.stock_quantity} units are available."}, status=status.HTTP_409_CONFLICT)
        else:
            item.quantity = quantity
            item.save(update_fields=["quantity", "updated_at"])
        return Response(session_payload(session))

    def delete(self, request, item_id):
        session = get_guest_session(request, create=False)
        if not session:
            return Response({"detail": "Cart session not found."}, status=status.HTTP_404_NOT_FOUND)
        CartItem.objects.filter(pk=item_id, session=session).delete()
        return Response(session_payload(session))


class WishlistItemsAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        session = get_guest_session(request)
        product_id = request.data.get("product_id")
        try:
            product_id = int(product_id)
        except (TypeError, ValueError):
            return Response({"detail": "product_id must be an integer."}, status=status.HTTP_400_BAD_REQUEST)
        product = get_object_or_404(Product, pk=product_id, is_active=True)
        WishlistItem.objects.get_or_create(session=session, product=product)
        return Response(session_payload(session))

    def delete(self, request, product_id):
        session = get_guest_session(request, create=False)
        if not session:
            return Response({"detail": "Wishlist session not found."}, status=status.HTTP_404_NOT_FOUND)
        WishlistItem.objects.filter(session=session, product_id=product_id).delete()
        return Response(session_payload(session))
