from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from .models import UserAccessLog
from .models import AdminProfile
from .models import AdminProfile, UserAccessLog
from django.utils import timezone

class AdminProfileInline(admin.StackedInline):
    model = AdminProfile
    can_delete = False
    verbose_name_plural = 'Two-Factor SMS Settings'

class CustomUserAdmin(DefaultUserAdmin):
    inlines = (AdminProfileInline,)
    list_display = ('username', 'email', 'get_date_joined', 'get_last_login', 'is_staff', 'is_active')
admin.site.site_header = "Administration"
admin.site.site_title = "Enterprise Operations"
admin.site.index_title = "Enterprise Operations Management"


admin.site.unregister(User)

@admin.register(User)
class CustomUserAdmin(DefaultUserAdmin):
    list_display = ('username', 'email', 'get_date_joined', 'get_last_login', 'is_staff', 'is_active')
    
    
    def get_date_joined(self, obj):
        return obj.date_joined.strftime("%B %d, %Y - %I:%M:%S %p")
    get_date_joined.short_description = "Account Created (Date/Time/Sec)"
    get_date_joined.admin_order_field = 'date_joined'


    def get_last_login(self, obj):
        if obj.last_login:
            return obj.last_login.strftime("%B %d, %Y - %I:%M:%S %p")
        return "Never"
    get_last_login.short_description = "Last Login (Date/Time/Sec)"
    get_last_login.admin_order_field = 'last_login'


@admin.register(UserAccessLog)
class UserAccessLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'display_timestamp', 'ip_address')
    list_filter = ('action', 'timestamp', 'user')
    search_fields = ('user__username', 'ip_address')
    readonly_fields = ('user', 'action', 'timestamp', 'ip_address')

    def display_timestamp(self, obj):
        if obj.timestamp:
            local_time = timezone.localtime(obj.timestamp)
            return local_time.strftime("%B %d, %Y - %I:%M:%S %p")
        return "-"
    display_timestamp.short_description = "Timestamp"
    
    def has_add_permission(self, request):
        return False  
from .models import AdminProfile

@admin.register(AdminProfile)
class AdminProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'is_2fa_enabled')
    list_editable = ('phone_number', 'is_2fa_enabled')
    search_fields = ('user__username', 'phone_number')