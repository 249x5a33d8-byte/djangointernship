"""
Products app — URL patterns.
"""
from django.urls import path
from . import views

urlpatterns = [
    # Categories
    path('categories/', views.CategoryListView.as_view(), name='category-list'),

    # Product CRUD
    path('', views.ProductListView.as_view(), name='product-list'),
    path('<int:pk>/', views.ProductDetailView.as_view(), name='product-detail'),
    path('create/', views.ProductCreateView.as_view(), name='product-create'),
    path('scrape/', views.ProductScrapeView.as_view(), name='product-scrape'),
    path('<int:pk>/update/', views.ProductUpdateView.as_view(), name='product-update'),
    path('<int:pk>/delete/', views.ProductDeleteView.as_view(), name='product-delete'),

    # Comparison
    path('compare/', views.ProductCompareView.as_view(), name='product-compare'),

    # Price History
    path('<int:product_id>/price-history/', views.PriceHistoryView.as_view(), name='price-history'),

    # Reviews
    path('<int:product_id>/review/', views.ReviewCreateView.as_view(), name='review-create'),

    # Wishlist
    path('wishlist/', views.WishlistListView.as_view(), name='wishlist-list'),
    path('wishlist/<int:pk>/', views.WishlistDeleteView.as_view(), name='wishlist-delete'),

    # Price Alerts
    path('alerts/', views.PriceAlertListView.as_view(), name='alert-list'),
    path('alerts/<int:pk>/', views.PriceAlertDeleteView.as_view(), name='alert-delete'),

    # Admin Analytics
    path('analytics/', views.ProductAnalyticsView.as_view(), name='product-analytics'),
]
