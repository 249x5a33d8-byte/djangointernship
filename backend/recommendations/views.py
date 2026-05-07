"""
Recommendations app — Views for product recommendations.
Recommends products based on category, rating, price range, and user history.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from products.models import Product, Wishlist
from products.serializers import ProductListSerializer
from django.db.models import Q, Avg


class RecommendationView(APIView):
    """
    GET /api/recommend/ — Personalized product recommendations.
    For authenticated users: based on wishlist categories and price range.
    For anonymous users: top-rated products across categories.
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        if request.user.is_authenticated:
            recommendations = self._get_personalized(request.user)
        else:
            recommendations = self._get_popular()

        serializer = ProductListSerializer(recommendations, many=True)
        return Response(serializer.data)

    def _get_personalized(self, user):
        """Get recommendations based on user's wishlist and history."""
        # Get categories from user's wishlist
        wishlist_categories = (
            Wishlist.objects.filter(user=user)
            .values_list('product__category', flat=True)
            .distinct()
        )

        # Get average price from wishlist
        avg_price = (
            Wishlist.objects.filter(user=user)
            .aggregate(avg=Avg('product__price'))['avg']
        )

        if wishlist_categories:
            # Recommend products from same categories, similar price range
            queryset = Product.objects.filter(
                category__in=wishlist_categories
            ).exclude(
                wishlisted_by__user=user  # Exclude already wishlisted
            ).order_by('-rating', '-review_count')

            if avg_price:
                # Prefer products within 50% price range
                queryset = queryset.filter(
                    price__gte=avg_price * 0.5,
                    price__lte=avg_price * 1.5,
                )

            return queryset[:12]

        return self._get_popular()

    def _get_popular(self):
        """Get popular products (fallback)."""
        return Product.objects.filter(
            rating__gte=3.5, in_stock=True
        ).order_by('-rating', '-review_count')[:12]


class SimilarProductsView(APIView):
    """
    GET /api/recommend/similar/<product_id>/ — Products similar to a given product.
    Based on same category, similar price range, and high ratings.
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request, product_id):
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"error": "Product not found."}, status=404)

        # Find similar products: same category, different vendor preferred, similar price
        price = float(product.price)
        similar = Product.objects.filter(
            category=product.category
        ).exclude(
            id=product.id
        ).filter(
            price__gte=price * 0.5,
            price__lte=price * 2.0,
        ).order_by('-rating')[:8]

        serializer = ProductListSerializer(similar, many=True)
        return Response(serializer.data)
