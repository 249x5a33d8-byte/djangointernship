from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from products.models import PriceAlert

class Command(BaseCommand):
    help = 'Checks all active price alerts and sends an email if triggered.'

    def handle(self, *args, **kwargs):
        self.stdout.write('Checking active price alerts...')
        alerts = PriceAlert.objects.filter(is_triggered=False)
        
        triggered_count = 0
        for alert in alerts:
            product = alert.product
            if product.price <= alert.target_price:
                # Alert condition met!
                self.send_alert_email(alert)
                alert.is_triggered = True
                alert.save()
                triggered_count += 1
                self.stdout.write(self.style.SUCCESS(f'Alert triggered for {product.name} (User: {alert.user.username})'))

        self.stdout.write(self.style.SUCCESS(f'Finished checking alerts. {triggered_count} alerts triggered and sent.'))

    def send_alert_email(self, alert):
        product = alert.product
        user = alert.user
        
        subject = f'Price Drop Alert! {product.name} is now under ₹{alert.target_price}'
        
        # Simple HTML content
        html_message = f"""
        <html>
            <body>
                <h2>Great news, {user.username}!</h2>
                <p>The product you are tracking has dropped below your target price.</p>
                <div style="border: 1px solid #ccc; padding: 15px; border-radius: 8px;">
                    <h3>{product.name}</h3>
                    <p>Current Price: <strong>₹{product.price}</strong> (Your target: ₹{alert.target_price})</p>
                    <a href="http://localhost:5173/products/{product.id}" style="background-color: #3b82f6; color: white; padding: 10px 15px; text-decoration: none; border-radius: 5px;">View Product</a>
                </div>
                <p>Happy Shopping,<br>IntelliShop Assistant</p>
            </body>
        </html>
        """
        plain_message = strip_tags(html_message)
        
        try:
            send_mail(
                subject,
                plain_message,
                'alerts@intellishop.local',
                [user.email],
                html_message=html_message,
                fail_silently=False,
            )
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Failed to send email to {user.email}: {str(e)}'))
