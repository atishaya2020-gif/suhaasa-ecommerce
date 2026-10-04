from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=90, unique=True)
    description = models.TextField(blank=True)
    image_url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "name"]
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Product(models.Model):
    sku = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=180)
    slug = models.SlugField(max_length=200, unique=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
    description = models.TextField()
    fabric = models.CharField(max_length=120, blank=True)
    color = models.CharField(max_length=80, blank=True)
    care = models.TextField(blank=True)
    dimensions = models.CharField(max_length=120, blank=True)
    highlights = models.JSONField(default=list, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    compare_at_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)])
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0, validators=[MinValueValidator(0), MaxValueValidator(5)])
    review_count = models.PositiveIntegerField(default=0)
    tag = models.CharField(max_length=80, blank=True)
    is_featured = models.BooleanField(default=False)
    is_new = models.BooleanField(default=False)
    is_bestseller = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-is_featured", "-created_at"]
        indexes = [
            models.Index(fields=["category", "is_active"]),
            models.Index(fields=["is_featured", "is_active"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.sku})"


class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="variants")
    name = models.CharField(max_length=80)
    sku = models.CharField(max_length=70, unique=True)
    stock_quantity = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["id"]
        constraints = [
            models.UniqueConstraint(fields=["product", "name"], name="unique_product_variant_name"),
        ]

    def __str__(self):
        return f"{self.product.name} — {self.name}"


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    url = models.URLField(blank=True)
    image = models.ImageField(upload_to="products/", blank=True)
    alt_text = models.CharField(max_length=180, blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    is_primary = models.BooleanField(default=False)

    class Meta:
        ordering = ["sort_order", "id"]

    def __str__(self):
        return f"{self.product.name} image {self.id}"
