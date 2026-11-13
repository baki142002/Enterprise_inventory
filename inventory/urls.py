from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='registration/password_reset_form.html'), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),
    path("products/", views.product_list, name="product_list"),
    path("products/add/", views.product_create, name="product_create"),
    path("products/<int:pk>/edit/", views.product_edit, name="product_edit"),
    path("categories/", views.category_list, name="category_list"),
    path("categories/add/", views.category_create, name="category_create"),
    path("suppliers/", views.supplier_list, name="supplier_list"),
    path("suppliers/add/", views.supplier_create, name="supplier_create"),
    path("transactions/", views.transaction_list, name="transaction_list"),
    path("transactions/add/", views.transaction_create, name="transaction_create"),
    path("sales/", views.sale_list, name="sale_list"),
    path("sales/add/", views.sale_create, name="sale_create"),
    path("forecast/", views.forecast, name="forecast"),
    path("reports/", views.reports, name="reports"),
    path('register/', views.register_view, name='register'),
    path('login/', views.admin_login_view, name='login'),
    path('login/verify-2fa/', views.admin_verify_2fa_view, name='admin_verify_2fa'),
    path('inventory/export-reorder/', views.export_reorder_csv, name='export_reorder_csv'),
    path('management/administration/', views.enterprise_admin_portal, name='custom_admin_portal'),
    path('management/users/add/', views.custom_create_user, name='custom_create_user'),
    path('management/password-change/', views.custom_change_password, name='custom_change_password'),
    path("management/users/", views.enterprise_user_list, name="enterprise_user_list"),
    path("management/users/<int:pk>/toggle/", views.enterprise_user_toggle_active, name="enterprise_user_toggle_active"),
    path("products/<int:pk>/delete/", views.product_delete, name="product_delete"),
    path("management/users/<int:user_id>/edit/", views.user_edit, name="user_edit"),
]
