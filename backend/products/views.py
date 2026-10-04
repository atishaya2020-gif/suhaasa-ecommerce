from rest_framework import generics
from rest_framework.filters import OrderingFilter, SearchFilter
from .models import Category, Product
from .serializers import CategorySerializer, ProductDetailSerializer, ProductListSerializer


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
