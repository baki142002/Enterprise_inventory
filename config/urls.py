from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from inventory import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("login/", auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("", views.dashboard, name="dashboard"),
    path('login/', views.admin_login_view, name='login'),
    path('login/verify-2fa/', views.admin_verify_2fa_view, name='admin_verify_2fa'),
    path("inventory/", include("inventory.urls")),
    path("products/<int:pk>/delete/", views.product_delete, name="product_delete"),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)