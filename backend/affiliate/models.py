"""
Affiliate app — Model to track affiliate link clicks.
"""
from django.db import models
from django.contrib.auth.models import User
from products.models import Product


class AffiliateClick(models.Model):
    """
    Tracks every click on an affiliate link.
    Used to calculate simulated commissions.
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='affiliate_clicks')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                             related_name='affiliate_clicks')
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, default='')
    clicked_at = models.DateTimeField(auto_now_add=True)

    # Simulated commission rate (5%)
    COMMISSION_RATE = 0.05

    class Meta:
        ordering = ['-clicked_at']

    def __str__(self):
        return f"Click: {self.product.name} at {self.clicked_at}"

    @property
    def estimated_commission(self):
        """Calculate simulated commission for this click."""
        return round(float(self.product.price) * self.COMMISSION_RATE, 2)
