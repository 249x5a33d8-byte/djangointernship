from django.contrib import admin
from .models import Prediction

@admin.register(Prediction)
class PredictionAdmin(admin.ModelAdmin):
    list_display = ['product', 'predicted_price', 'predicted_date', 'algorithm', 'confidence']
    list_filter = ['algorithm', 'predicted_date']
