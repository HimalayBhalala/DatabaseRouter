from django.conf import settings
import threading

_thread_locals = threading.local()

class MultiTenantRouter:
    """
    A router to control database operations for multi-tenant setup
    """
    
    def db_for_read(self, model, **hints):
        """Suggest the database to read from."""
        
        admin_apps = ['admin', 'auth', 'contenttypes', 'sessions']
        
        if (model._meta.app_label in admin_apps or 
            model._meta.model_name == 'brand'):
            return 'default'
        
        if model._meta.app_label == 'app':
            brand_name = getattr(_thread_locals, 'brand_name', None) or getattr(settings, 'CURRENT_BRAND_NAME', None)
            if brand_name and brand_name != 'default' and brand_name in settings.DATABASES:
                return brand_name
        return 'default'

    def db_for_write(self, model, **hints):
        """Suggest the database to write to."""

        admin_apps = ['admin', 'auth', 'contenttypes', 'sessions']
        if (model._meta.app_label in admin_apps or 
            model._meta.model_name == 'brand'):
            return 'default'
            
        if model._meta.app_label == 'app':
            brand_name = getattr(_thread_locals, 'brand_name', None) or getattr(settings, 'CURRENT_BRAND_NAME', None)
            if brand_name and brand_name != 'default' and brand_name in settings.DATABASES:
                return brand_name
        return 'default'

def set_brand_context(brand_name):
    """Set brand context for current thread"""
    _thread_locals.brand_name = brand_name
    settings.CURRENT_BRAND_NAME = brand_name

def get_brand_context():
    """Get brand context for current thread"""
    return getattr(_thread_locals, 'brand_name', 'default') 