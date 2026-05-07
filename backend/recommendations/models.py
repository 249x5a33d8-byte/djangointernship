"""
Recommendations app — No extra models needed.
Uses Product and user history from other apps.
"""
from django.db import models
# This app uses Product model from products app
# No additional models needed — recommendations are computed on-the-fly
