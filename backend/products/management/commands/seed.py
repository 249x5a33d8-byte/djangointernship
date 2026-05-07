import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.models import User
from products.models import Category, Product, PriceHistory

class Command(BaseCommand):
    help = 'Seeds the database with sample categories, products, and price history'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding database...')

        # Create Categories
        categories_data = ['Electronics', 'Laptops', 'Smartphones', 'Headphones', 'Home Appliances']
        categories = {}
        for cat_name in categories_data:
            cat, created = Category.objects.get_or_create(name=cat_name, slug=cat_name.lower().replace(' ', '-'))
            categories[cat_name] = cat
        
        # Create a test admin user if not exists
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
            self.stdout.write('Created admin user: admin/admin123')

        # Create Products
        products_data = [
            {'name': 'MacBook Pro 14"', 'category': 'Laptops', 'base_price': 1999.99},
            {'name': 'Dell XPS 13', 'category': 'Laptops', 'base_price': 1399.99},
            {'name': 'iPhone 15 Pro', 'category': 'Smartphones', 'base_price': 999.99},
            {'name': 'Samsung Galaxy S24 Ultra', 'category': 'Smartphones', 'base_price': 1199.99},
            {'name': 'Sony WH-1000XM5', 'category': 'Headphones', 'base_price': 399.99},
            {'name': 'AirPods Pro 2', 'category': 'Headphones', 'base_price': 249.99},
            {'name': 'LG C3 OLED TV', 'category': 'Electronics', 'base_price': 1499.99},
            {'name': 'Dyson V15 Detect', 'category': 'Home Appliances', 'base_price': 749.99},
        ]

        for p_data in products_data:
            cat = categories[p_data['category']]
            
            # Create one for Amazon, one for Flipkart
            vendors = ['Amazon', 'Flipkart']
            for vendor in vendors:
                vendor_price = p_data['base_price'] + random.uniform(-20, 50)
                product, created = Product.objects.get_or_create(
                    name=p_data['name'],
                    vendor=vendor,
                    defaults={
                        'category': cat,
                        'description': f"A great {p_data['name']}.",
                        'price': round(vendor_price, 2),
                        'original_price': round(vendor_price * 1.1, 2),
                        'affiliate_link': f"https://{vendor.lower()}.com/dp/{random.randint(100000, 999999)}",
                        'image_url': f"https://via.placeholder.com/400x400?text={p_data['name'].replace(' ', '+')}",
                        'rating': round(random.uniform(3.5, 4.9), 1),
                        'review_count': random.randint(100, 5000),
                    }
                )

                if created:
                    # Generate 6 months of price history
                    base_p = p_data['base_price']
                    today = timezone.now().date()
                    for i in range(180, -1, -5): # every 5 days
                        history_date = today - timedelta(days=i)
                        
                        # Add some random walk / noise to the price
                        noise = random.uniform(-base_p * 0.05, base_p * 0.05)
                        hist_price = round(base_p + noise, 2)
                        
                        PriceHistory.objects.get_or_create(
                            product=product,
                            recorded_at=history_date,
                            defaults={'price': hist_price}
                        )
        
        self.stdout.write(self.style.SUCCESS('Database successfully seeded!'))

