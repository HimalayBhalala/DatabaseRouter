from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from django.apps import apps
from .db_router import set_brand_context, get_brand_context

class TenantMiddleware(MiddlewareMixin):
    """
    Middleware to detect tenant/brand and set database context
    """
    
    def process_request(self, request):
        """
        Detect brand from request and set database context
        """        
        if (request.path.startswith('/admin/') or 
            request.path.startswith('/favicon.ico')):
            brand_name = 'default'
        else:
            brand_name = self.get_brand_from_request(request)
        
        set_brand_context(brand_name)
        
        request.brand_name = brand_name
        
        return None
    
    def get_brand_from_request(self, request):
        """
        Extract brand name from various sources
        Priority: Header > Subdomain > URL parameter > Default
        """
        brand_name = request.META.get('HTTP_X_BRAND_NAME')
        if brand_name:
            brand_name = brand_name.lower()
            is_valid = self.is_valid_brand(brand_name)
            if is_valid:
                return brand_name.strip()

        return 'default'
    
    def is_valid_brand(self, brand_name):
        """
        Check if brand exists and is active
        """
        try:
            if brand_name == 'default':
                return True

            if brand_name not in settings.DATABASES:
                return False

            Brand = apps.get_model('app', 'Brand')
            brand = Brand.objects.using('default').get(
                brand_name=brand_name, 
                is_active=True
            )
            return True
        except Exception as e:
            return False

def get_current_brand():
    """
    Utility function to get current brand from thread-local storage
    """
    return get_brand_context()