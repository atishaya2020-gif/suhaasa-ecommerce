from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils.text import slugify

from products.models import Category, Product, ProductImage, ProductVariant


IMAGES = {
    "kurtaA": "https://images.unsplash.com/photo-1760287364328-e30221615f2e?auto=format&fit=crop&w=1200&q=88",
    "kurtaB": "https://images.unsplash.com/photo-1743229995505-d6374996df1c?auto=format&fit=crop&w=1200&q=88",
    "kurtaC": "https://images.unsplash.com/photo-1742800786544-e935375035e3?auto=format&fit=crop&w=1200&q=88",
    "kurtaD": "https://images.unsplash.com/photo-1742800788220-1e42256d6022?auto=format&fit=crop&w=1200&q=88",
    "kurtaE": "https://images.unsplash.com/photo-1762780700690-3fbb53fcd4e5?auto=format&fit=crop&w=1200&q=88",
    "kurtaF": "https://images.unsplash.com/photo-1769063382706-8156b3b33eac?auto=format&fit=crop&w=1200&q=88",
    "bedsheetA": "https://images.unsplash.com/photo-1631049421450-348ccd7f8949?auto=format&fit=crop&w=1200&q=88",
    "bedsheetB": "https://images.unsplash.com/photo-1627383837817-d4fc073f72e8?auto=format&fit=crop&w=1200&q=88",
    "bedsheetC": "https://images.unsplash.com/photo-1589154587853-da70e391f38a?auto=format&fit=crop&w=1200&q=88",
    "bedsheetD": "https://images.unsplash.com/photo-1648395957856-ed5a83bb200e?auto=format&fit=crop&w=1200&q=88",
    "towelA": "https://images.unsplash.com/photo-1788059317676-28c0eda2a736?auto=format&fit=crop&w=1200&q=88",
    "towelB": "https://images.unsplash.com/photo-1702432631344-3fb6b053fb3f?auto=format&fit=crop&w=1200&q=88",
    "towelC": "https://images.unsplash.com/photo-1565775913442-79337915b869?auto=format&fit=crop&w=1200&q=88",
    "towelD": "https://images.unsplash.com/photo-1620733723572-11c53f73a416?auto=format&fit=crop&w=1200&q=88",
}

DESCRIPTION_BY_NAME = {
    'Sandalwood Handblock Kurta': 'A softly structured handblock kurta in a warm, earthy palette — designed for easy days, slow mornings and evenings that stretch a little longer.',
    'Rosewood Printed Bedsheet': 'A generous, breathable bedsheet with a quietly expressive print, made to bring warmth and texture to everyday spaces.',
    'Clay Bloom Cotton Towel Set': 'A plush everyday towel set with a calm clay-inspired tone and a soft hand feel for the rituals that start and end your day.',
    'Madder Floral Kurta Set': 'A floral kurta set with an easy silhouette and a softly vintage palette, created for occasions that call for something special without feeling overdone.',
    'Neem Leaf Block Kurta': 'A calm botanical-inspired kurta with an easy fit and a muted palette that works from morning errands to evening plans.',
    'Indigo Dusk Kurta': 'A deep indigo silhouette with quiet detailing and a relaxed shape, made for understated occasions.',
    'Terracotta Bloom Kurta': 'Warm terracotta tones and a softly patterned finish give this everyday kurta its distinctive character.',
    'Ivory Everyday Kurta': 'An understated ivory staple designed to pair effortlessly with the rest of your wardrobe.',
    'Sage Garden Bedsheet': 'A soft sage palette and gentle botanical rhythm bring a calm, lived-in feeling to the bedroom.',
    'Indigo Stripe Bedsheet': 'A timeless indigo bedding layer with subtle stripe texture for a room that feels collected rather than decorated.',
    'Sandstone Everyday Bedsheet': 'Warm neutral bedding designed to sit quietly beneath cushions, throws and the rhythms of everyday life.',
    'Rose Petal Towel Set': 'A soft rose-toned towel set with a plush hand feel and an understated woven texture.',
    'Sage Spa Towel Set': 'Fresh sage tones and soft loops bring a quiet spa feeling to everyday bath rituals.',
    'Ivory Cloud Towel Set': 'A clean ivory towel set that keeps the bathroom palette warm, simple and timeless.',
}

PRODUCTS = [
    ("SH-KRT-001", "Sandalwood Handblock Kurta", "Kurtas", 1899, 2299, "New", "100% cotton", "Sandalwood", ["S", "M", "L", "XL"], 18, 4.8, 24, None, "Gentle machine wash with similar colours. Dry in shade.", ["Handblock-inspired print", "Relaxed everyday silhouette", "Breathable cotton"], "kurtaA", "kurtaB", True, True, False),
    ("SH-HOM-001", "Rosewood Printed Bedsheet", "Bedsheets", 1499, 1899, "Bestseller", "100% cotton", "Rosewood", ["Double"], 31, 4.9, 42, "225 × 270 cm", "Machine wash cold. Tumble dry low or line dry.", ["Soft breathable weave", "Generous double-bed size", "Easy everyday care"], "bedsheetA", "bedsheetB", True, False, True),
    ("SH-TWL-001", "Clay Bloom Cotton Towel Set", "Towels", 799, None, "Soft cotton", "Premium cotton", "Clay", ["Set of 2"], 27, 4.7, 18, "70 × 140 cm each", "Machine wash cold. Avoid bleach.", ["Soft looped texture", "Quick-drying weave", "Set of two bath towels"], "towelA", "towelB", True, False, False),
    ("SH-KRT-002", "Madder Floral Kurta Set", "Kurtas", 2299, 2799, "Limited", "100% cotton", "Madder Rose", ["S", "M", "L", "XL"], 9, 4.9, 16, None, "Gentle machine wash. Wash dark colours separately.", ["Coordinated two-piece set", "Soft floral motif", "Occasion-ready comfort"], "kurtaB", "kurtaC", True, False, False),
    ("SH-KRT-003", "Neem Leaf Block Kurta", "Kurtas", 1799, None, "Everyday", "100% cotton", "Neem Green", ["S", "M", "L", "XL"], 22, 4.6, 13, None, "Gentle wash inside out. Dry in shade.", ["Botanical motif", "Easy regular fit", "Soft everyday cotton"], "kurtaC", "kurtaD", False, False, False),
    ("SH-KRT-004", "Indigo Dusk Kurta", "Kurtas", 2099, 2499, "New", "Cotton slub", "Indigo", ["S", "M", "L", "XL"], 14, 4.8, 21, None, "Cold wash separately. Do not wring.", ["Textured cotton slub", "Relaxed silhouette", "Deep indigo palette"], "kurtaD", "kurtaE", True, True, False),
    ("SH-KRT-005", "Terracotta Bloom Kurta", "Kurtas", 1999, None, "Handblock", "Handblock cotton", "Terracotta", ["S", "M", "L", "XL"], 12, 4.7, 11, None, "Gentle hand wash recommended. Dry in shade.", ["Handblock-inspired pattern", "Warm terracotta tone", "Lightweight cotton"], "kurtaE", "kurtaF", False, False, False),
    ("SH-KRT-006", "Ivory Everyday Kurta", "Kurtas", 1699, None, "Essential", "Cotton voile", "Ivory", ["S", "M", "L", "XL"], 25, 4.8, 29, None, "Gentle wash. Iron on low heat.", ["Wardrobe essential", "Lightweight voile", "Easy-to-style neutral"], "kurtaF", "kurtaA", False, False, False),
    ("SH-HOM-002", "Sage Garden Bedsheet", "Bedsheets", 1699, 1999, "New", "100% cotton", "Sage", ["Double"], 19, 4.8, 20, "225 × 270 cm", "Machine wash cold. Dry in shade.", ["Botanical-inspired print", "Soft sage palette", "Breathable cotton"], "bedsheetB", "bedsheetC", True, True, False),
    ("SH-HOM-003", "Indigo Stripe Bedsheet", "Bedsheets", 1599, None, "Classic", "Percale cotton", "Indigo", ["Double"], 16, 4.7, 15, "225 × 270 cm", "Machine wash cold. Wash dark colours separately.", ["Classic stripe texture", "Crisp percale feel", "Everyday double-bed size"], "bedsheetC", "bedsheetD", False, False, False),
    ("SH-HOM-004", "Sandstone Everyday Bedsheet", "Bedsheets", 1399, 1699, "Best value", "100% cotton", "Sandstone", ["Double"], 34, 4.6, 32, "225 × 270 cm", "Machine wash cold. Tumble dry low.", ["Warm neutral colour", "Soft cotton weave", "Easy-care essential"], "bedsheetD", "bedsheetA", False, False, False),
    ("SH-TWL-002", "Rose Petal Towel Set", "Towels", 899, 1099, "Soft cotton", "Combed cotton", "Rose Petal", ["Set of 2"], 21, 4.8, 17, "70 × 140 cm each", "Machine wash cold. Avoid fabric softener.", ["Combed cotton", "Plush hand feel", "Set of two bath towels"], "towelB", "towelC", False, False, False),
    ("SH-TWL-003", "Sage Spa Towel Set", "Towels", 849, None, "New", "Premium cotton", "Sage", ["Set of 2"], 15, 4.7, 12, "70 × 140 cm each", "Machine wash cold. Dry thoroughly between uses.", ["Spa-inspired palette", "Soft cotton loops", "Quick everyday drying"], "towelC", "towelD", False, True, False),
    ("SH-TWL-004", "Ivory Cloud Towel Set", "Towels", 799, None, "Essential", "Ring-spun cotton", "Ivory", ["Set of 2"], 29, 4.9, 35, "70 × 140 cm each", "Machine wash cold. Avoid bleach.", ["Ring-spun cotton", "Timeless ivory tone", "Soft everyday essential"], "towelD", "towelA", True, False, False),
]


class Command(BaseCommand):
    help = "Seed the approved SUHAASA demo catalogue into the local database."

    def handle(self, *args, **options):
        category_map = {}
        for index, name in enumerate(["Kurtas", "Bedsheets", "Towels"], start=1):
            category, _ = Category.objects.update_or_create(
                slug=slugify(name),
                defaults={"name": name, "is_active": True, "sort_order": index},
            )
            category_map[name] = category

        for row in PRODUCTS:
            (sku, name, category_name, price, old_price, tag, fabric, color, sizes, stock,
             rating, review_count, dimensions, care, highlights, image_a, image_b,
             featured, is_new, bestseller) = row

            product, _ = Product.objects.update_or_create(
                sku=sku,
                defaults={
                    "name": name,
                    "slug": slugify(name),
                    "category": category_map[category_name],
                    "description": DESCRIPTION_BY_NAME.get(name, f"{name} — a SUHAASA catalogue product."),
                    "fabric": fabric,
                    "color": color,
                    "care": care,
                    "dimensions": dimensions or "",
                    "highlights": highlights,
                    "price": Decimal(price),
                    "compare_at_price": Decimal(old_price) if old_price else None,
                    "rating": Decimal(str(rating)),
                    "review_count": review_count,
                    "tag": tag,
                    "is_featured": featured,
                    "is_new": is_new,
                    "is_bestseller": bestseller,
                    "is_active": True,
                },
            )

            product.variants.all().delete()
            for position, size in enumerate(sizes, start=1):
                ProductVariant.objects.create(
                    product=product,
                    name=size,
                    sku=f"{sku}-{size.replace(' ', '-').upper()}",
                    stock_quantity=stock if position == 1 else stock,
                    is_active=True,
                )

            product.images.all().delete()
            for position, key in enumerate([image_a, image_b], start=1):
                ProductImage.objects.create(
                    product=product,
                    url=IMAGES[key],
                    alt_text=name,
                    sort_order=position,
                    is_primary=position == 1,
                )

        self.stdout.write(self.style.SUCCESS(f"Seeded {len(PRODUCTS)} SUHAASA demo products."))
