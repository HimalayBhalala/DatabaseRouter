# From rest_framework 
from rest_framework.exceptions import AuthenticationFailed
from rest_framework import permissions

from marketplace import settings
import jwt

from app.models import Users, BrandAdmin
from .middleware import get_current_brand


class JWTAuthorization(permissions.BasePermission):

    @staticmethod
    def decode_jwt_token(token):
        try:
            decoded_token = jwt.decode(token, settings.SIMPLE_JWT['SIGNING_KEY'], algorithms=['HS256'])
            return decoded_token
        except:
            return None
    
    
    def authenticate(self, request):
        try:
            auth_header = request.headers.get('Authorization')
            if not auth_header:
                return None

            token = auth_header.split(' ')[-1]
            decoded_token = self.decode_jwt_token(token)

            if decoded_token:
                user_id = decoded_token['user_id']
                try:
                    user = Users.objects.filter(userid=user_id).first()
                    return user
                except Users.DoesNotExist:
                    return None
            return None
        except Exception as e:
            raise AuthenticationFailed(f"Token verification failed: {str(e)}")

    def has_permission(self, request, view):
        user = self.authenticate(request)

        request.user = user  # Set the authenticated user in the request
        return user is not None
    


class AdminJWTAuthorization(permissions.BasePermission):

    @staticmethod
    def decode_jwt_token(token):
        try:
            decoded_token = jwt.decode(token, settings.SIMPLE_JWT['SIGNING_KEY'], algorithms=['HS256'])
            return decoded_token
        except:
            return None
    
    
    def authenticate(self, request):
        try:
            auth_header = request.headers.get('Authorization')
            if not auth_header:
                return None

            token = auth_header.split(' ')[-1]
            decoded_token = self.decode_jwt_token(token)

            if decoded_token:
                user_id = decoded_token['user_id']
                try:
                    user = Users.objects.filter(userid=user_id).first()
                    return user
                except Users.DoesNotExist:
                    return None
            return None
        except Exception as e:
            raise AuthenticationFailed(f"Token verification failed: {str(e)}")

    def has_permission(self, request, view):
        if not request.user or not hasattr(request.user, 'userid'):
            return False
        
        brand_name = get_current_brand()
        
        try:
            brand_admin = BrandAdmin.objects.using('default').get(
                email=request.user.email,
                is_active=True,
                brand_name=brand_name
            )
            return True
        except BrandAdmin.DoesNotExist:
            return False