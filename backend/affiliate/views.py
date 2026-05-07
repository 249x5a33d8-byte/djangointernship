"""
Affiliate app — Views for click tracking, redirect, and stats.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from django.shortcuts import redirect as django_redirect
from django.db.models import Count, Sum, F
from products.models import Product
from .models import AffiliateClick


class AffiliateRedirectView(APIView):
    """
    GET /api/affiliate/redirect/<product_id>/ — Track click and redirect to affiliate URL.
    This simulates the affiliate marketing flow:
    1. User clicks "Buy Now" on a product
    2. System records the click
    3. User is redirected to the affiliate URL
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request, product_id):
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"error": "Product not found."}, status=404)

        # Record the click
        AffiliateClick.objects.create(
            product=product,
            user=request.user if request.user.is_authenticated else None,
            ip_address=self._get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
        )

        # Redirect to affiliate link (or product URL)
        redirect_url = product.affiliate_link or f'https://www.{product.vendor.lower()}.in/'
        return Response({
            'redirect_url': redirect_url,
            'message': 'Click recorded successfully.',
            'product_id': product.id,
        })

    def _get_client_ip(self, request):
        """Extract client IP from request."""
        x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded:
            return x_forwarded.split(',')[0]
        return request.META.get('REMOTE_ADDR')


class AffiliateStatsView(APIView):
    """
    GET /api/affiliate/stats/ — Admin: affiliate click statistics and commissions.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # Overall stats
        total_clicks = AffiliateClick.objects.count()

        # Clicks per product (top 10)
        product_clicks = (
            AffiliateClick.objects
            .values('product__id', 'product__name', 'product__price', 'product__vendor')
            .annotate(click_count=Count('id'))
            .order_by('-click_count')[:10]
        )

        # Calculate total estimated commission
        clicks = AffiliateClick.objects.select_related('product').all()
        total_commission = sum(c.estimated_commission for c in clicks)

        # Clicks per vendor
        vendor_clicks = (
            AffiliateClick.objects
            .values('product__vendor')
            .annotate(click_count=Count('id'))
            .order_by('-click_count')
        )

        # Recent clicks (last 20)
        recent = AffiliateClick.objects.select_related('product', 'user')[:20]
        recent_data = [
            {
                'product': c.product.name,
                'user': c.user.username if c.user else 'Anonymous',
                'commission': c.estimated_commission,
                'clicked_at': c.clicked_at.isoformat(),
            }
            for c in recent
        ]

        return Response({
            'total_clicks': total_clicks,
            'total_commission': round(total_commission, 2),
            'commission_rate': '5%',
            'product_clicks': list(product_clicks),
            'vendor_clicks': list(vendor_clicks),
            'recent_clicks': recent_data,
        })
