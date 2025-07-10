# Include Django Packages
from django.conf import settings

# Include DRF Packages
from rest_framework.exceptions import AuthenticationFailed
from rest_framework import permissions

# Include From the Project Directory
from app.models import Users
from .middleware import get_current_brand

# Include Built-in Package
import jwt


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

            brand_name = decoded_token['brand_name']

            if decoded_token:
                user_id = decoded_token['user_id']
                try:

                    if brand_name != get_current_brand():
                        raise AuthenticationFailed("You have not able to access another brand.")
                    
                    user = Users.objects.using(brand_name).filter(userid=user_id, brand_name=brand_name).first()
                    
                    if not user.is_active:
                        raise ValueError("Your account is deactivated to not able to access it.")
                    request.brand_name = brand_name

                    return user
                except Users.DoesNotExist:
                    return None
            return None
        except Exception as e:
            raise AuthenticationFailed(f"Token verification failed: {str(e)}")

    def has_permission(self, request, view):
        user = self.authenticate(request)
        request.user = user
        return user is not None
