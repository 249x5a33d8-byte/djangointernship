from django.urls import path
from . import views

urlpatterns = [
    path('redirect/<int:product_id>/', views.AffiliateRedirectView.as_view(), name='affiliate-redirect'),
    path('stats/', views.AffiliateStatsView.as_view(), name='affiliate-stats'),
]
