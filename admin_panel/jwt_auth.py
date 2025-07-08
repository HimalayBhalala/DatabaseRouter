from django.conf import settings
from rest_framework import permissions
from rest_framework.exceptions import AuthenticationFailed
from app.models import BrandAdmin
import jwt

class AdminJWTAuthorization(permissions.BasePermission):
    
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
            brand_name = decoded_token['brand_name']
            
            # Get the admin from database
            admin = BrandAdmin.objects.filter(id=admin_id, brand_name=brand_name, is_active=True).first()
            
            if not admin:
                return False
            
            request.admin = admin
            request.brand_name = brand_name
            
            return True
            
        except Exception as e:
            return False