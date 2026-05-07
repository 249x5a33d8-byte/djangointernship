# Intelligent Shopping Assistant using Machine Learning

A complete final year college project that helps users make smart shopping decisions. This local-first application tracks products across Amazon and Flipkart, predicts future prices using Machine Learning, and recommends the best time to buy.

## Features
- **Price Predictions:** A Scikit-learn Random Forest model trained on historical data predicts future prices up to 30 days ahead.
- **Smart Recommendations:** The system advises whether to "Buy Now" or "Wait" based on predicted price drops.
- **Product Tracking:** Users can browse products, add them to their Wishlist, and set Price Alerts.
- **Affiliate Integration:** Simulates tracking of affiliate clicks and commissions for administrators.
- **Modern UI:** Built with React, Tailwind CSS v4, and Lucide Icons for a beautiful, responsive, glass-morphism aesthetic.

## Tech Stack
- **Frontend:** React 18, Vite, Tailwind CSS v4, Chart.js, React Router
- **Backend:** Django 5, Django REST Framework, Simple JWT
- **Machine Learning:** Pandas, NumPy, Scikit-learn, Joblib
- **Database:** SQLite (local dev only)

## Installation & Setup

Ensure you have Python 3.13+ and Node.js 22+ installed.

### 1. Backend Setup
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# Run migrations and seed data
python manage.py migrate
python manage.py seed

# Train the ML model
python train_model.py

# Start the server (runs on http://localhost:8000)
python manage.py runserver
```

### 2. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

Open `http://localhost:5173` in your browser.
Test Admin Login: `admin` / `admin123`

## Project Structure
- `/backend`: Django REST API, Scikit-learn training scripts, and SQLite database.
- `/frontend`: React SPA with routing, AuthContext, and Chart.js integration.
- `/backend/ml_models`: Saved `.joblib` Random Forest model.

## Note
This project is built for LOCAL demonstration. No cloud deployments, AWS, or Docker are included to keep it lightweight for a college defense.
