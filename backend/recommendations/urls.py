from django.urls import path
from . import views

urlpatterns = [
    path('', views.RecommendationView.as_view(), name='recommendation-list'),
    path('similar/<int:product_id>/', views.SimilarProductsView.as_view(), name='similar-products'),
]
