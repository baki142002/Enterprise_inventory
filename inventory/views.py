from datetime import timedelta
from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Sum, F, DecimalField, ExpressionWrapper
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from .models import Product, Category, Supplier, StockTransaction, Sale
from .forms import ProductForm, CategoryForm, SupplierForm, StockTransactionForm, SaleForm
from django.contrib.auth import authenticate, login
from .models import SMSVerificationCode
from .sms_service import send_email_otp
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Sum
from .models import Product, Sale
from django.http import HttpResponse
from .models import Product
import csv
import random


@login_required
def export_reorder_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="reorder_stock_report.csv"'

    writer = csv.writer(response)
    writer.writerow(['Product Code', 'Product Name', 'Current Stock', 'Reorder Level', 'Suggested Restock Qty', 'Supplier'])

    low_stock_items = Product.objects.filter(quantity__lte=models.F('reorder_level'))

    for item in low_stock_items:
        needed_qty = (item.reorder_level * 2) - item.quantity
        supplier_name = item.supplier.name if item.supplier else "N/A"
        writer.writerow([
            item.code if hasattr(item, 'code') else item.id,
            item.name,
            item.quantity,
            item.reorder_level,
            max(needed_qty, 1),
            supplier_name
        ])

    return response


def forecast_view(request):
    today = timezone.now().date()
    thirty_days_ago = today - timedelta(days=30)
    
    products = Product.objects.all()
    forecast_data = []

    for product in products:
        # Aggregate quantity sold over last 30 days
        total_sold_30d = Sale.objects.filter(
            product=product,
            sale_date__gte=thirty_days_ago
        ).aggregate(total=Sum('quantity'))['total'] or 0

        # Average Daily Consumption (ADC)
        daily_velocity = Decimal(total_sold_30d) / Decimal(30)

        # Days until inventory depletes
        if daily_velocity > 0:
            days_until_stockout = int(product.quantity / daily_velocity)
            stockout_date = today + timedelta(days=days_until_stockout)
        else:
            days_until_stockout = None
            stockout_date = None

        # Recommended replenishment quantity (Buffer for 14-day lead time)
        lead_time_days = 14
        suggested_reorder = max(0, int((daily_velocity * lead_time_days) + product.reorder_level - product.quantity))

        # Risk level determination
        if product.quantity <= product.reorder_level:
            urgency = 'CRITICAL'
        elif days_until_stockout is not None and days_until_stockout <= 7:
            urgency = 'WARNING'
        else:
            urgency = 'STABLE'

        forecast_data.append({
            'product': product,
            'daily_velocity': round(daily_velocity, 2),
            'days_until_stockout': days_until_stockout,
            'stockout_date': stockout_date,
            'suggested_reorder': suggested_reorder,
            'urgency': urgency,
        })

    context = {
        'forecast_data': forecast_data,
        'today': today,
    }
    return render(request, 'inventory/forecast.html', context)


def admin_login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Check user has an email address
            recipient_email = user.email or 'lemuelbasco12345@gmail.com'

            # Generate 6-digit code
            otp_code = f"{random.randint(100000, 999999)}"

            # Save in database
            SMSVerificationCode.objects.create(
                user=user,
                code=otp_code,
                is_used=False
            )

            # Send via Gmail
            send_email_otp(recipient_email, otp_code, user.username)

            # Store in session and route to verification
            request.session['pre_2fa_user_id'] = user.id
            request.session['pre_2fa_email'] = recipient_email
            return redirect('admin_verify_2fa')
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, 'registration/login.html')


def admin_verify_2fa_view(request):
    user_id = request.session.get('pre_2fa_user_id')
    if not user_id:
        return redirect('login')

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return redirect('login')

    # Phone number display for masked UI (e.g. 0985****420)
    if request.method == 'POST':
        # 1. Grab code from single input or multiple split boxes
        entered_code = request.POST.get('code', '').strip()
        if not entered_code:
            # Check if template used 6 separate input boxes (otp_1 to otp_6 or digit_1 to digit_6)
            parts = [request.POST.get(f'otp_{i}', '') or request.POST.get(f'digit_{i}', '') for i in range(1, 7)]
            entered_code = ''.join(parts).strip()

        print(f"--> [DEBUG 2FA] Submitted code: '{entered_code}' for user: {user.username}")

        # 2. Look up the latest unused code for this user
        verification = SMSVerificationCode.objects.filter(
            user=user,
            code=entered_code,
            is_used=False
        ).order_by('-created_at').first()

        # Fallback check if code was already marked used on double-submit
        if not verification:
            verification = SMSVerificationCode.objects.filter(
                user=user,
                code=entered_code
            ).order_by('-created_at').first()

        if verification:
            # Mark code as used
            verification.is_used = True
            verification.save()

            # Clean session
            if 'pre_2fa_user_id' in request.session:
                del request.session['pre_2fa_user_id']

            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)

            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('/')
        else:
            messages.error(request, "Invalid or expired verification code.")

    return render(request, 'inventory/verify_2fa.html', {
        'user': user
    })



@login_required
def dashboard(request):
    products = Product.objects.filter(active=True)
    sales_7 = Sale.objects.filter(sold_at__gte=timezone.now()-timedelta(days=7))
    context = {
        "product_count": products.count(),
        "low_stock": products.filter(quantity__lte=F("reorder_level")).count(),
        "inventory_value": sum((p.stock_value for p in products), Decimal("0.00")),
        "sales_total": sum((s.total for s in sales_7), Decimal("0.00")),
        "recent_transactions": StockTransaction.objects.select_related("product").order_by("-created_at")[:6],
        "low_products": products.filter(quantity__lte=F("reorder_level")).select_related("category")[:6],
        "recent_sales": Sale.objects.select_related("product").order_by("-sold_at")[:5],
    }
    return render(request, "inventory/dashboard.html", context)

@login_required
def product_list(request):
    q = request.GET.get("q", "")
    products = Product.objects.select_related("category","supplier").all().order_by("name")
    if q: products = products.filter(name__icontains=q) | products.filter(sku__icontains=q)
    return render(request, "inventory/product_list.html", {"products": products, "q": q})

@login_required
def product_create(request):
    form = ProductForm(request.POST or None)
    if form.is_valid():
        form.save(); messages.success(request, "Product created."); return redirect("product_list")
    return render(request, "inventory/form.html", {"form": form, "title": "Add product"})

@login_required
def product_edit(request, pk):
    obj = get_object_or_404(Product, pk=pk)
    form = ProductForm(request.POST or None, instance=obj)
    if form.is_valid():
        form.save(); messages.success(request, "Product updated."); return redirect("product_list")
    return render(request, "inventory/form.html", {"form": form, "title": "Edit product"})

@login_required
def category_list(request):
    return render(request, "inventory/category_list.html", {"categories": Category.objects.all().order_by("name")})

@login_required
def category_create(request):
    form = CategoryForm(request.POST or None)
    if form.is_valid():
        form.save(); messages.success(request, "Category created."); return redirect("category_list")
    return render(request, "inventory/form.html", {"form": form, "title": "Add category"})

@login_required
def supplier_list(request):
    return render(request, "inventory/supplier_list.html", {"suppliers": Supplier.objects.all().order_by("name")})

@login_required
def supplier_create(request):
    form = SupplierForm(request.POST or None)
    if form.is_valid():
        form.save(); messages.success(request, "Supplier created."); return redirect("supplier_list")
    return render(request, "inventory/form.html", {"form": form, "title": "Add supplier"})

@login_required
def transaction_list(request):
    rows = StockTransaction.objects.select_related("product","created_by").order_by("-created_at")
    return render(request, "inventory/transaction_list.html", {"rows": rows[:200]})

@login_required
def transaction_create(request):
    form = StockTransactionForm(request.POST or None)
    if form.is_valid():
        with transaction.atomic():
            row = form.save(commit=False)
            product = Product.objects.select_for_update().get(pk=row.product_id)
            if row.transaction_type == StockTransaction.OUT and product.quantity < row.quantity:
                form.add_error("quantity", "Not enough stock available.")
            else:
                if row.transaction_type == StockTransaction.IN: product.quantity += row.quantity
                elif row.transaction_type == StockTransaction.OUT: product.quantity -= row.quantity
                else: product.quantity = row.quantity
                product.save(update_fields=["quantity"])
                row.created_by = request.user
                row.save()
                messages.success(request, "Inventory transaction recorded.")
                return redirect("transaction_list")
    return render(request, "inventory/form.html", {"form": form, "title": "Record inventory transaction"})

@login_required
def sale_list(request):
    sales = Sale.objects.select_related("product","recorded_by").order_by("-sold_at")
    return render(request, "inventory/sale_list.html", {"sales": sales[:200]})

@login_required
def sale_create(request):
    form = SaleForm(request.POST or None)
    if form.is_valid():
        with transaction.atomic():
            sale = form.save(commit=False)
            product = Product.objects.select_for_update().get(pk=sale.product_id)
            if product.quantity < sale.quantity:
                form.add_error("quantity", "Not enough stock available.")
            else:
                product.quantity -= sale.quantity
                product.save(update_fields=["quantity"])
                sale.recorded_by = request.user
                sale.save()
                StockTransaction.objects.create(product=product, transaction_type=StockTransaction.OUT,
                    quantity=sale.quantity, reference=sale.reference or "Sale", notes="Automatic stock deduction",
                    created_by=request.user)
                messages.success(request, "Sale recorded and inventory updated.")
                return redirect("sale_list")
    return render(request, "inventory/form.html", {"form": form, "title": "Record sale"})

@login_required
def forecast(request):
    # Simple transparent baseline: average daily sales over the last 30 days, projected 30 days.
    since = timezone.now() - timedelta(days=30)
    rows = []
    for product in Product.objects.filter(active=True).order_by("name"):
        sold = Sale.objects.filter(product=product, sold_at__gte=since).aggregate(total=Sum("quantity"))["total"] or 0
        daily = Decimal(sold) / Decimal("30")
        predicted = int(round(float(daily * Decimal("30"))))
        suggested = max(0, predicted + product.reorder_level - product.quantity)
        rows.append({"product": product, "sold": sold, "daily": daily.quantize(Decimal("0.01")),
                     "forecast": predicted, "suggested": suggested})
    return render(request, "inventory/forecast.html", {"rows": rows})

@login_required
def reports(request):
    sales = Sale.objects.order_by("-sold_at")[:100]
    total_sales = sum((s.total for s in sales), Decimal("0.00"))
    return render(request, "inventory/reports.html", {"sales": sales, "total_sales": total_sales})
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            # Default new staff to is_staff=False or True depending on your policy
            user.save()
            messages.success(request, f"Account created for {user.username}! You can now sign in.")
            return redirect('login')
    else:
        form = UserCreationForm()
        
    return render(request, 'inventory/registers.html', {'form': form})