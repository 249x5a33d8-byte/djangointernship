"""
Predictions app — Model to store price predictions.
"""
from django.db import models
from products.models import Product


class Prediction(models.Model):
    """Stores ML-generated price predictions for products."""
    ALGORITHM_CHOICES = [
        ('linear_regression', 'Linear Regression'),
        ('random_forest', 'Random Forest'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='predictions')
    predicted_price = models.DecimalField(max_digits=10, decimal_places=2)
    predicted_date = models.DateField()
    algorithm = models.CharField(max_length=30, choices=ALGORITHM_CHOICES, default='random_forest')
    confidence = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    recommendation = models.CharField(max_length=100, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['predicted_date']

    def __str__(self):
        return f"{self.product.name} → ₹{self.predicted_price} on {self.predicted_date}"
