"""
Products app — Views for product listing, detail, search, compare, wishlist, alerts.
"""
from rest_framework import generics, permissions, status, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q
from .models import Category, Product, PriceHistory, Review, Wishlist, PriceAlert
from .serializers import (
    CategorySerializer, ProductListSerializer, ProductDetailSerializer,
    ProductCreateSerializer, ReviewSerializer, PriceHistorySerializer,
    WishlistSerializer, PriceAlertSerializer,
)


# ============================================================
# Category Views
# ============================================================
class CategoryListView(generics.ListAPIView):
    """GET /api/products/categories/ — List all categories."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = None  # Return all categories without pagination


# ============================================================
# Product Views
# ============================================================
class ProductListView(generics.ListAPIView):
    """
    GET /api/products/ — List products with search, filter, and sort.
    Query params: search, category, vendor, min_price, max_price, ordering
    """
    serializer_class = ProductListSerializer

    def get_queryset(self):
        queryset = Product.objects.all()
        params = self.request.query_params

        # Search by name or description
        search = params.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(description__icontains=search)
            )

        # Filter by category
        category = params.get('category', '')
        if category:
            queryset = queryset.filter(category__slug=category)

        # Filter by vendor (Amazon / Flipkart)
        vendor = params.get('vendor', '')
        if vendor:
            queryset = queryset.filter(vendor__iexact=vendor)

        # Filter by price range
        min_price = params.get('min_price')
        max_price = params.get('max_price')
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)

        # Filter by rating
        min_rating = params.get('min_rating')
        if min_rating:
            queryset = queryset.filter(rating__gte=min_rating)

        # Sorting
        ordering = params.get('ordering', '-created_at')
        if ordering in ['price', '-price', 'rating', '-rating', 'name', '-name', '-created_at']:
            queryset = queryset.order_by(ordering)

        return queryset


class ProductDetailView(generics.RetrieveAPIView):
    """GET /api/products/<id>/ — Product detail with price history and reviews."""
    queryset = Product.objects.all()
    serializer_class = ProductDetailSerializer


class ProductCreateView(generics.CreateAPIView):
    """POST /api/products/create/ — Admin: create a product."""
    queryset = Product.objects.all()
    serializer_class = ProductCreateSerializer
    permission_classes = [permissions.IsAuthenticated]


class ProductUpdateView(generics.UpdateAPIView):
    """PUT /api/products/<id>/update/ — Admin: update a product."""
    queryset = Product.objects.all()
    serializer_class = ProductCreateSerializer
    permission_classes = [permissions.IsAuthenticated]


class ProductDeleteView(generics.DestroyAPIView):
    """DELETE /api/products/<id>/delete/ — Admin: delete a product."""
    queryset = Product.objects.all()
    permission_classes = [permissions.IsAuthenticated]

class ProductScrapeView(APIView):
    """POST /api/products/scrape/ — Scrape product details from URL."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        url = request.data.get('url')
        if not url:
            return Response({'error': 'URL is required'}, status=status.HTTP_400_BAD_REQUEST)

        from .scraper import scrape_product
        result = scrape_product(url)

        if not result['success']:
            return Response({'error': result['error']}, status=status.HTTP_400_BAD_REQUEST)

        # Automatically create or find the product
        data = result['data']
        # Assign to first category as default for now
        category = Category.objects.first()
        
        product, created = Product.objects.get_or_create(
            name=data['name'],
            defaults={
                'description': f"Product scraped from {data['vendor']}",
                'price': data['price'],
                'image_url': data['image_url'],
                'vendor': data['vendor'],
                'affiliate_link': data['url'],
                'category': category
            }
        )

        serializer = ProductDetailSerializer(product)
        return Response({
            'message': 'Product scraped and added successfully' if created else 'Product already exists',
            'product': serializer.data
        }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


# ============================================================
# Product Comparison
# ============================================================
class ProductCompareView(APIView):
    """
    GET /api/products/compare/?ids=1,2,3 — Compare multiple products.
    Returns full details for up to 4 products side-by-side.
    """
    def get(self, request):
        ids_param = request.query_params.get('ids', '')
        if not ids_param:
            return Response({"error": "Please provide product IDs."}, status=400)

        try:
            ids = [int(x.strip()) for x in ids_param.split(',') if x.strip()]
        except ValueError:
            return Response({"error": "Invalid product IDs."}, status=400)

        products = Product.objects.filter(id__in=ids[:4])  # Max 4 products
        serializer = ProductDetailSerializer(products, many=True)
        return Response(serializer.data)


# ============================================================
# Price History
# ============================================================
class PriceHistoryView(generics.ListAPIView):
    """GET /api/products/<product_id>/price-history/ — Price history for a product."""
    serializer_class = PriceHistorySerializer
    pagination_class = None

    def get_queryset(self):
        product_id = self.kwargs['product_id']
        return PriceHistory.objects.filter(product_id=product_id)


# ============================================================
# Reviews
# ============================================================
class ReviewCreateView(APIView):
    """POST /api/products/<product_id>/review/ — Add a review."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, product_id):
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"error": "Product not found."}, status=404)

        # Check if user already reviewed
        if Review.objects.filter(product=product, user=request.user).exists():
            return Response({"error": "You already reviewed this product."}, status=400)

        serializer = ReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(product=product, user=request.user)

        # Update product review count and average rating
        reviews = Review.objects.filter(product=product)
        product.review_count = reviews.count()
        avg = reviews.values_list('rating', flat=True)
        product.rating = round(sum(avg) / len(avg), 2) if avg else 0
        product.save()

        return Response(serializer.data, status=201)


# ============================================================
# Wishlist
# ============================================================
class WishlistListView(generics.ListCreateAPIView):
    """GET/POST /api/products/wishlist/ — User's wishlist."""
    serializer_class = WishlistSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class WishlistDeleteView(generics.DestroyAPIView):
    """DELETE /api/products/wishlist/<id>/ — Remove from wishlist."""
    serializer_class = WishlistSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user)


# ============================================================
# Price Alerts
# ============================================================
class PriceAlertListView(generics.ListCreateAPIView):
    """GET/POST /api/products/alerts/ — User's price alerts."""
    serializer_class = PriceAlertSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        alerts = PriceAlert.objects.filter(user=self.request.user)
        # Check triggers on every fetch
        for alert in alerts:
            alert.check_trigger()
        return alerts

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class PriceAlertDeleteView(generics.DestroyAPIView):
    """DELETE /api/products/alerts/<id>/ — Remove a price alert."""
    serializer_class = PriceAlertSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return PriceAlert.objects.filter(user=self.request.user)


# ============================================================
# Admin: Product Analytics
# ============================================================
class ProductAnalyticsView(APIView):
    """GET /api/products/analytics/ — Admin: product statistics."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        from affiliate.models import AffiliateClick
        total_products = Product.objects.count()
        amazon_count = Product.objects.filter(vendor='Amazon').count()
        flipkart_count = Product.objects.filter(vendor='Flipkart').count()
        categories = Category.objects.count()
        total_clicks = AffiliateClick.objects.count()

        # Top products by clicks
        from django.db.models import Count
        top_products = (
            Product.objects.annotate(click_count=Count('affiliate_clicks'))
            .order_by('-click_count')[:5]
        )

        return Response({
            'total_products': total_products,
            'amazon_count': amazon_count,
            'flipkart_count': flipkart_count,
            'categories': categories,
            'total_clicks': total_clicks,
            'top_products': [
                {'id': p.id, 'name': p.name, 'clicks': p.click_count}
                for p in top_products
            ]
        })
