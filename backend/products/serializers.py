"""
Products app — Serializers for all product-related models.
"""
from rest_framework import serializers
from .models import Category, Product, PriceHistory, Review, Wishlist, PriceAlert


class CategorySerializer(serializers.ModelSerializer):
    product_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'image_url', 'product_count']

    def get_product_count(self, obj):
        return obj.products.count()


class PriceHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PriceHistory
        fields = ['id', 'price', 'recorded_at']


class ReviewSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'username', 'rating', 'comment', 'created_at']
        read_only_fields = ['id', 'username', 'created_at']


class ProductListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for product listing pages."""
    category_name = serializers.CharField(source='category.name', read_only=True)
    discount_percentage = serializers.ReadOnlyField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'image_url', 'price', 'original_price',
            'rating', 'review_count', 'vendor', 'category', 'category_name',
            'discount_percentage', 'in_stock', 'affiliate_link',
        ]


class ProductDetailSerializer(serializers.ModelSerializer):
    """Full serializer with price history and reviews for detail page."""
    category_name = serializers.CharField(source='category.name', read_only=True)
    discount_percentage = serializers.ReadOnlyField()
    price_history = PriceHistorySerializer(many=True, read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'image_url', 'price', 'original_price',
            'rating', 'review_count', 'vendor', 'affiliate_link',
            'category', 'category_name', 'discount_percentage',
            'in_stock', 'created_at', 'price_history', 'reviews',
        ]


class ProductCreateSerializer(serializers.ModelSerializer):
    """Serializer for admin product creation/editing."""
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'image_url', 'price', 'original_price',
            'rating', 'review_count', 'vendor', 'affiliate_link',
            'category', 'in_stock',
        ]


class WishlistSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Wishlist
        fields = ['id', 'product', 'product_id', 'target_price', 'added_at']
        read_only_fields = ['id', 'added_at']


class PriceAlertSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = PriceAlert
        fields = ['id', 'product', 'product_id', 'target_price', 'is_triggered', 'created_at']
        read_only_fields = ['id', 'is_triggered', 'created_at']
