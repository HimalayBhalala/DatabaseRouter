from django.contrib import admin
from .models import Brand, Users, Tasks, BrandAdmin

@admin.register(Brand)
class BrandDataAdmin(admin.ModelAdmin):
    list_display = ('brand_name', 'database_name', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('brand_name', 'subdomain')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Users)
class UsersAdmin(admin.ModelAdmin):
    list_display = ('email', 'firstname', 'surname','is_active', 'is_staff', 'created_at')
    list_filter = ('is_active', 'is_staff', 'created_at')
    search_fields = ('email', 'firstname', 'surname')
    readonly_fields = ('created_at', 'updated_at', 'password')
    
    def get_queryset(self, request):
        return super().get_queryset(request).using('default')

@admin.register(Tasks)
class TasksAdmin(admin.ModelAdmin):
    list_display = ('saved_search', 'userid','min_price', 'max_price', 'active', 'created_at')
    list_filter = ('active', 'created_at')
    search_fields = ('saved_search', 'userid__email', 'postcode')
    readonly_fields = ('created_at', 'updated_at')
    
    def get_queryset(self, request):
        return super().get_queryset(request).using('default')

@admin.register(BrandAdmin)
class BrandUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'firstname', 'surname','is_active',
    'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('email', 'firstname', 'surname')
    readonly_fields = ('created_at', 'updated_at', 'password')
    
    def get_queryset(self, request):
        return super().get_queryset(request).using('default')
