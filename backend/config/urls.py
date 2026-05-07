"""
Main URL configuration for Intelligent Shopping Assistant.
All API endpoints are registered here.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Django admin panel
    path('admin/', admin.site.urls),

    # API endpoints
    path('api/auth/', include('users.urls')),
    path('api/products/', include('products.urls')),
    path('api/predict/', include('predictions.urls')),
    path('api/recommend/', include('recommendations.urls')),
    path('api/affiliate/', include('affiliate.urls')),
]
