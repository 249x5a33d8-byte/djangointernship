"""
Predictions app — Core ML predictor logic.
Loads trained models and generates price predictions.
"""
import os
import numpy as np
from datetime import date, timedelta
from django.conf import settings

try:
    import joblib
    JOBLIB_AVAILABLE = True
except ImportError:
    JOBLIB_AVAILABLE = False


def load_model(algorithm='random_forest'):
    """Load a trained ML model from disk."""
    if not JOBLIB_AVAILABLE:
        return None

    model_path = os.path.join(settings.ML_MODELS_DIR, f'{algorithm}_model.joblib')
    if os.path.exists(model_path):
        return joblib.load(model_path)
    return None


def predict_prices(product, days_ahead=30):
    """
    Predict future prices for a product using the trained ML model.

    Args:
        product: Product instance
        days_ahead: Number of days to predict into the future

    Returns:
        List of dicts with 'date', 'predicted_price', 'algorithm'
    """
    model = load_model('random_forest')

    # If no trained model exists, use a simple simulation
    if model is None:
        return _simulate_predictions(product, days_ahead)

    predictions = []
    current_price = float(product.price)
    original_price = float(product.original_price or product.price)
    discount_pct = ((original_price - current_price) / original_price * 100) if original_price > 0 else 0
    rating = float(product.rating)
    review_count = product.review_count
    today = date.today()

    for day in range(1, days_ahead + 1):
        future_date = today + timedelta(days=day)
        # Features: [original_price, discount_pct, rating, review_count, day_of_week, day_of_month, days_ahead]
        features = np.array([[
            original_price,
            discount_pct,
            rating,
            review_count,
            future_date.weekday(),
            future_date.day,
            day
        ]])

        predicted = model.predict(features)[0]
        predictions.append({
            'date': future_date.isoformat(),
            'predicted_price': round(float(predicted), 2),
            'algorithm': 'random_forest',
        })

    return predictions


def _simulate_predictions(product, days_ahead=30):
    """
    Fallback: simulate price predictions when no ML model is available.
    Uses a realistic pattern with slight downward trend and fluctuation.
    """
    predictions = []
    current_price = float(product.price)
    today = date.today()
    np.random.seed(product.id)  # Deterministic per product

    for day in range(1, days_ahead + 1):
        future_date = today + timedelta(days=day)
        # Simulate a slight downward trend with noise
        trend = -0.001 * day  # Small daily decrease
        noise = np.random.normal(0, 0.01)  # 1% noise
        weekend_effect = -0.005 if future_date.weekday() >= 5 else 0  # Sales on weekends
        month_end_effect = -0.02 if future_date.day >= 25 else 0  # Month-end sales

        factor = 1 + trend + noise + weekend_effect + month_end_effect
        predicted_price = current_price * factor

        predictions.append({
            'date': future_date.isoformat(),
            'predicted_price': round(max(predicted_price, current_price * 0.7), 2),
            'algorithm': 'simulation',
        })

    return predictions


def get_recommendation(product, predictions):
    """
    Generate buy/wait recommendation based on predictions and historical data.

    Returns:
        dict with 'action', 'message', 'best_price', 'best_date', 'savings', 'best_month'
    """
    from products.models import PriceHistory
    from django.db.models import Avg
    from django.db.models.functions import ExtractMonth
    import calendar

    current_price = float(product.price)

    # Calculate historically best month to buy
    history = PriceHistory.objects.filter(product=product).annotate(
        month=ExtractMonth('recorded_at')
    ).values('month').annotate(avg_price=Avg('price')).order_by('avg_price')

    best_month = None
    if history.exists():
        best_month_num = history.first()['month']
        best_month = calendar.month_name[best_month_num]

    if not predictions:
        return {
            'action': 'buy_now',
            'message': 'No prediction data available. Buy now if needed.',
            'best_price': current_price,
            'best_date': date.today().isoformat(),
            'savings': 0,
            'best_month': best_month,
        }

    # Find the lowest predicted price
    best = min(predictions, key=lambda p: p['predicted_price'])
    best_price = best['predicted_price']
    savings = round(current_price - best_price, 2)
    savings_pct = round((savings / current_price) * 100, 1) if current_price > 0 else 0

    if savings > 0 and savings_pct >= 3:
        days_to_wait = (date.fromisoformat(best['date']) - date.today()).days
        return {
            'action': 'wait',
            'message': f'Wait {days_to_wait} days! Price may drop to ₹{best_price:,.0f} (save {savings_pct}%).',
            'best_price': best_price,
            'best_date': best['date'],
            'savings': savings,
            'savings_pct': savings_pct,
            'best_month': best_month,
        }
    else:
        return {
            'action': 'buy_now',
            'message': 'Good time to buy! Prices are expected to stay stable or increase.',
            'best_price': current_price,
            'best_date': date.today().isoformat(),
            'savings': 0,
            'savings_pct': 0,
            'best_month': best_month,
        }
