from django.urls import path
from . import views

urlpatterns = [
    path('<int:product_id>/', views.PredictPriceView.as_view(), name='predict-price'),
    path('stats/', views.PredictionStatsView.as_view(), name='prediction-stats'),
]
