from decimal import Decimal

from django.db import transaction
from django.db.models import F, Sum
from django.core.exceptions import ValidationError
from rest_framework import generics, status
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Category, InventoryAdjustment, Product, ProductVariant
from .services import adjust_inventory
from .serializers import (
    CategorySerializer,
    InventoryAdjustmentSerializer,
    InventoryVariantSerializer,
    ProductDetailSerializer,
    ProductListSerializer,
)


class CategoryListAPIView(generics.ListAPIView):
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer


class ProductListAPIView(generics.ListAPIView):
    queryset = Product.objects.filter(is_active=True).select_related("category").prefetch_related("images", "variants")
    serializer_class = ProductListSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["name", "sku", "description", "fabric", "color", "tag", "category__name"]
    ordering_fields = ["price", "rating", "created_at", "name"]
    ordering = ["-is_featured", "-created_at"]

    def get_queryset(self):
        queryset = super().get_queryset()
        category = self.request.query_params.get("category")
        if category:
            queryset = queryset.filter(category__slug=category)
        return queryset


class ProductDetailAPIView(generics.RetrieveAPIView):
    queryset = Product.objects.filter(is_active=True).select_related("category").prefetch_related("images", "variants")
    serializer_class = ProductDetailSerializer
    lookup_field = "slug"


class InventoryVariantListAPIView(generics.ListAPIView):
    permission_classes = [IsAdminUser]
    queryset = ProductVariant.objects.select_related("product", "product__category").order_by("product__name", "name")
    serializer_class = InventoryVariantSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["product__name", "product__sku", "name", "sku"]
    ordering_fields = ["stock_quantity", "low_stock_threshold", "product__name"]
    ordering = ["product__name", "name"]

    def get_queryset(self):
        queryset = super().get_queryset()
        stock_status = self.request.query_params.get("status")
        if stock_status == "out_of_stock":
            queryset = queryset.filter(stock_quantity=0)
        elif stock_status == "low_stock":
            queryset = queryset.filter(stock_quantity__gt=0, stock_quantity__lte=F("low_stock_threshold"))
        elif stock_status == "in_stock":
            queryset = queryset.filter(stock_quantity__gt=F("low_stock_threshold"))
        return queryset


class InventoryAdjustmentAPIView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        variant_id = request.data.get("variant_id")
        quantity_change = request.data.get("quantity_change")
        reason = request.data.get("reason")
        note = str(request.data.get("note", "")).strip()

        if not variant_id:
            return Response({"detail": "variant_id is required."}, status=status.HTTP_400_BAD_REQUEST)
        if quantity_change is None:
            return Response({"detail": "quantity_change is required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            quantity_change = int(quantity_change)
        except (TypeError, ValueError):
            return Response({"detail": "quantity_change must be an integer."}, status=status.HTTP_400_BAD_REQUEST)
        if quantity_change == 0:
            return Response({"detail": "quantity_change cannot be zero."}, status=status.HTTP_400_BAD_REQUEST)

        valid_reasons = dict(InventoryAdjustment.REASON_CHOICES)
        if reason not in valid_reasons:
            return Response({"detail": "Invalid adjustment reason.", "allowed_reasons": list(valid_reasons.keys())}, status=status.HTTP_400_BAD_REQUEST)

        try:
            variant, adjustment = adjust_inventory(
                variant_id=variant_id,
                quantity_change=quantity_change,
                reason=reason,
                note=note,
                adjusted_by=request.user,
            )
        except ProductVariant.DoesNotExist:
            return Response({"detail": "Product variant not found."}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as exc:
            message = exc.messages[0] if exc.messages else "Invalid inventory adjustment."
            if "negative" in message.lower():
                return Response({"detail": message, "available_stock": ProductVariant.objects.get(pk=variant_id).stock_quantity}, status=status.HTTP_409_CONFLICT)
            return Response({"detail": message}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {
                "variant": InventoryVariantSerializer(variant, context={"request": request}).data,
                "adjustment": InventoryAdjustmentSerializer(adjustment, context={"request": request}).data,
            },
            status=status.HTTP_201_CREATED,
        )


class InventoryAdjustmentListAPIView(generics.ListAPIView):
    permission_classes = [IsAdminUser]
    queryset = InventoryAdjustment.objects.select_related("variant", "variant__product", "adjusted_by").order_by("-created_at", "-id")
    serializer_class = InventoryAdjustmentSerializer
    filter_backends = [SearchFilter]
    search_fields = [
        "variant__product__name", "variant__product__sku", "variant__name",
        "variant__sku", "note", "adjusted_by__username",
    ]


class InventoryDashboardAPIView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        variants = ProductVariant.objects.filter(is_active=True, product__is_active=True)
        total_variants = variants.count()
        out_of_stock = variants.filter(stock_quantity=0).count()
        low_stock = variants.filter(stock_quantity__gt=0, stock_quantity__lte=F("low_stock_threshold")).count()
        in_stock = variants.filter(stock_quantity__gt=F("low_stock_threshold")).count()
        total_units = variants.aggregate(total=Sum("stock_quantity"))["total"] or 0
        inventory_value = Decimal("0.00")
        for variant in variants.select_related("product"):
            inventory_value += variant.product.price * variant.stock_quantity

        return Response({
            "total_products": Product.objects.filter(is_active=True).count(),
            "total_variants": total_variants,
            "in_stock_variants": in_stock,
            "low_stock_variants": low_stock,
            "out_of_stock_variants": out_of_stock,
            "total_units": total_units,
            "inventory_value": inventory_value,
        })
