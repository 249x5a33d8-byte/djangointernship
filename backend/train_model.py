import os
import django
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error
import joblib

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.conf import settings
from products.models import Product, PriceHistory

def train_model():
    print("Loading data from database...")
    histories = PriceHistory.objects.select_related('product').all()
    
    if not histories.exists():
        print("No price history found. Please run seed script first.")
        return

    data = []
    for h in histories:
        product = h.product
        original_price = float(product.original_price or product.price)
        current_price = float(product.price)
        discount_pct = ((original_price - current_price) / original_price * 100) if original_price > 0 else 0
        rating = float(product.rating)
        review_count = product.review_count
        
        # We need a target value (e.g. price N days ahead). For simplicity in training:
        # Let's say we are predicting the current `h.price` based on these features and date info.
        data.append({
            'original_price': original_price,
            'discount_pct': discount_pct,
            'rating': rating,
            'review_count': review_count,
            'day_of_week': h.recorded_at.weekday(),
            'day_of_month': h.recorded_at.day,
            'days_ahead': 1, # dummy feature to match predictor shape
            'target_price': float(h.price)
        })

    df = pd.DataFrame(data)
    print(f"Loaded {len(df)} records.")

    # Features: [original_price, discount_pct, rating, review_count, day_of_week, day_of_month, days_ahead]
    X = df[['original_price', 'discount_pct', 'rating', 'review_count', 'day_of_week', 'day_of_month', 'days_ahead']]
    y = df['target_price']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    print("Training Random Forest Regressor...")
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # Evaluate
    predictions = model.predict(X_test)
    mse = mean_squared_error(y_test, predictions)
    mae = mean_absolute_error(y_test, predictions)
    print(f"Model Evaluation - MSE: {mse:.2f}, MAE: {mae:.2f}")

    # Save model
    os.makedirs(settings.ML_MODELS_DIR, exist_ok=True)
    model_path = os.path.join(settings.ML_MODELS_DIR, 'random_forest_model.joblib')
    joblib.dump(model, model_path)
    print(f"Model saved to {model_path}")

if __name__ == '__main__':
    train_model()
