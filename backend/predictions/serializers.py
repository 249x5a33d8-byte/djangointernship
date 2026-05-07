"""
Predictions app — Serializers.
"""
from rest_framework import serializers
from .models import Prediction


class PredictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prediction
        fields = ['id', 'product', 'predicted_price', 'predicted_date',
                  'algorithm', 'confidence', 'recommendation', 'created_at']
