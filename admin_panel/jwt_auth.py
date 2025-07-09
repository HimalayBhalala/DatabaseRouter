# Include a Django packeage
from django.conf import settings

# Include DRF Packeges
from rest_framework import permissions
from rest_framework.exceptions import AuthenticationFailed

# Include using a Project Directory
from app.models import BrandAdmin

# Include third-party packages
import jwt


class AdminJWTAuthorization(permissions.BasePermission):

    """
        Admin Based JwtAuthentication
    """
    
    @staticmethod
    def decode_jwt_token(token):
        try:
            decoded_token = jwt.decode(token, settings.SIMPLE_JWT['SIGNING_KEY'], algorithms=['HS256'])
            return decoded_token
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
        except Exception:
            return None
    
    def authenticate(self, request):
        """
        This method should be in an Authentication class, not Permission class.
        Moving the logic to has_permission method.
        """
        try:
            auth_header = request.headers.get('Authorization')
            if not auth_header:
                return None
            
            token = auth_header.split(' ')[-1]
            decoded_token = self.decode_jwt_token(token)
            
            if decoded_token:
                admin_id = decoded_token['user_id']
                brand_name = decoded_token['brand_name']
                try:
                    admin = BrandAdmin.objects.filter(id=admin_id, is_active=True, brand_name=brand_name).first()
                    return admin
                except BrandAdmin.DoesNotExist:
                    return None
            return None
        except Exception as e:
            raise AuthenticationFailed(f"Token verification failed: {str(e)}")
    
    def has_permission(self, request, view):
        try:
            auth_header = request.headers.get('Authorization')
            if not auth_header:
                return False
            
            token = auth_header.split(' ')[-1]
            decoded_token = self.decode_jwt_token(token)
            
            if not decoded_token:
                return False
            
            admin_id = decoded_token['user_id']
            brand_name = decoded_token.get('brand_name') 
            
            if not brand_name:
                return False
                        
            admin = BrandAdmin.objects.filter(id=admin_id, brand_name=brand_name, is_active=True).first()
            
            if not admin:
                return False
            
            request.admin = admin
            request.brand_name = brand_name
            request.admin_name = admin.firstname
            
            return True
            
        except Exception as e:
            return False