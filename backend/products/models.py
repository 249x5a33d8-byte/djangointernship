"""
Products app — Models for Category, Product, PriceHistory, Review, Wishlist, PriceAlert.
This is the core data model for the shopping assistant.
"""
from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    """Product category (e.g., Electronics, Clothing, Books)."""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True, default='')
    image_url = models.URLField(blank=True, default='')

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class Product(models.Model):
    """
    Product model — stores products from Amazon and Flipkart.
    Each product has a vendor, price, rating, and affiliate link.
    """
    VENDOR_CHOICES = [
        ('Amazon', 'Amazon'),
        ('Flipkart', 'Flipkart'),
    ]

    name = models.CharField(max_length=300)
    description = models.TextField(blank=True, default='')
    image_url = models.URLField(blank=True, default='')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    original_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    review_count = models.IntegerField(default=0)
    vendor = models.CharField(max_length=20, choices=VENDOR_CHOICES)
    affiliate_link = models.URLField(blank=True, default='')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    in_stock = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.vendor})"

    @property
    def discount_percentage(self):
        """Calculate discount percentage from original price."""
        if self.original_price and self.original_price > 0:
            return round(((self.original_price - self.price) / self.original_price) * 100, 1)
        return 0


class PriceHistory(models.Model):
    """
    Tracks daily price changes for each product.
    Used by the ML model to predict future prices.
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='price_history')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    recorded_at = models.DateField()

    class Meta:
        ordering = ['recorded_at']
        verbose_name_plural = 'Price histories'
        unique_together = ['product', 'recorded_at']

    def __str__(self):
        return f"{self.product.name} — ₹{self.price} on {self.recorded_at}"


class Review(models.Model):
    """User review for a product."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['product', 'user']  # One review per user per product

    def __str__(self):
        return f"{self.user.username} → {self.product.name}: {self.rating}★"


class Wishlist(models.Model):
    """User's wishlist — products they want to track."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='wishlisted_by')
    target_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'product']
        ordering = ['-added_at']

    def __str__(self):
        return f"{self.user.username} → {self.product.name}"


class PriceAlert(models.Model):
    """
    Price alert — notifies user when product drops below target price.
    For local demo, we simply flag it on the dashboard.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='price_alerts')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='alerts')
    target_price = models.DecimalField(max_digits=10, decimal_places=2)
    is_triggered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'product']
        ordering = ['-created_at']

    def __str__(self):
        return f"Alert: {self.product.name} < ₹{self.target_price}"

    def check_trigger(self):
        """Check if current price is below target and trigger alert."""
        if self.product.price <= self.target_price:
            self.is_triggered = True
            self.save()
        return self.is_triggered
