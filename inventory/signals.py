from django.db.models.signals import post_save
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserAccessLog
from .models import Sale, StockTransaction, Product, UserAccessLog

@receiver(post_save, sender=Sale)
def monitor_stock_after_sale(sender, instance, created, **kwargs):
    if created:
        product = instance.product
        # Deduct quantity from catalog
        product.quantity -= instance.quantity
        product.save(update_fields=['quantity'])

        # Automated threshold check
        if product.quantity <= product.reorder_level:
            UserAccessLog.objects.create(
                user=instance.cashier if hasattr(instance, 'cashier') else None,
                action=f"AUTOMATED ALERT: Product '{product.name}' hit low stock ({product.quantity} remaining). Reorder suggested.",
                ip_address="127.0.0.1"
            )


def get_client_ip(request):
    """Utility to capture user IP address"""
    if request:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')
    return None

# 1. Triggered whenever a new user account is created
@receiver(post_save, sender=User)
def log_user_registration(sender, instance, created, **kwargs):
    if created:
        UserAccessLog.objects.create(
            user=instance,
            action='REGISTER'
        )

# 2. Triggered every time a user logs in
@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    UserAccessLog.objects.create(
        user=user,
        action='LOGIN',
        ip_address=get_client_ip(request)
    )
    