"""
Predictions app — Views for price prediction API.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from products.models import Product, PriceHistory
from .predictor import predict_prices, get_recommendation


class PredictPriceView(APIView):
    """
    GET /api/predict/<product_id>/ — Get price prediction for a product.
    Returns predicted prices, recommendation, and chart data.
    """
    def get(self, request, product_id):
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"error": "Product not found."}, status=404)

        days = int(request.query_params.get('days', 30))
        days = min(days, 90)  # Max 90 days

        # Generate predictions
        predictions = predict_prices(product, days_ahead=days)

        # Get recommendation
        recommendation = get_recommendation(product, predictions)

        # Get historical prices for chart
        history = PriceHistory.objects.filter(product=product).order_by('recorded_at')
        historical_data = [
            {'date': h.recorded_at.isoformat(), 'price': float(h.price)}
            for h in history
        ]

        return Response({
            'product_id': product.id,
            'product_name': product.name,
            'current_price': float(product.price),
            'predictions': predictions,
            'recommendation': recommendation,
            'historical_prices': historical_data,
        })


class PredictionStatsView(APIView):
    """
    GET /api/predict/stats/ — Admin: ML prediction statistics.
    """
    def get(self, request):
        from .models import Prediction
        total_predictions = Prediction.objects.count()
        buy_now = Prediction.objects.filter(recommendation__icontains='buy').count()
        wait = Prediction.objects.filter(recommendation__icontains='wait').count()

        return Response({
            'total_predictions': total_predictions,
            'buy_now_count': buy_now,
            'wait_count': wait,
            'model_info': {
                'algorithms': ['Linear Regression', 'Random Forest'],
                'features': ['original_price', 'discount_pct', 'rating', 'review_count',
                             'day_of_week', 'day_of_month', 'days_ahead'],
            }
        })
