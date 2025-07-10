# Include Django Packages
from django.shortcuts import render

# Include DjangoRestFrameWork Packages
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

# Include From the Project Folder
from .models import *
from .serializers import *
from app.models import Brand, Users
from .jwt_auth import AdminJWTAuthorization
from app.utils import APIValidateView
from app.serializers import ContactSerializer

# Include Built-in Package
import bcrypt

# Create your views here.
class ListOfBrandView(APIValidateView):
    
    def get(self,request):

        brand_list = {}
        brands = Brand.objects.all()

        if not brands:
            return {}
        
        for brand in brands:
            brand_list[brand.id] = brand.brand_name

        return Response({
            "status": "success",
            "data":brand_list
        }, status=status.HTTP_200_OK)


class UserRegistrationView(APIValidateView):
    """
    Register a new user. 
    """

    def post(self, request, brand_id):
        brand = Brand.objects.filter(brand_id=brand_id).first()

        if not brand:
            return Response({
                "status":"error",
                "message": "Your included brand not exits"
            }, status=status.HTTP_400_BAD_REQUEST)
                    
        brand_name = brand.brand_name

        serializer_data = BrandAdminSerializer(data=request.data, context={'brand_name': brand_name})

        serializer_data.is_valid(raise_exception=True)

        serializer_data.save()

        return Response({
            'status': 'success',
            'message': "You've been included as an admin, but access to the admin panel requires approval from the main admin",
        }, status=status.HTTP_201_CREATED)


class AdminLoginView(APIValidateView):
    """
    Login user and return JWT tokens
    """

    def post(self, request, brand_id):

        email = request.data.get('email')
        password = request.data.get('password')

        brand = Brand.objects.filter(brand_id=brand_id).first()

        if not brand:
            return Response({
                "status":"error",
                "message": "Your included brand not exits"
            }, status=status.HTTP_400_BAD_REQUEST)
                    
        brand_name = brand.brand_name

        # Validate required fields
        if not all([email, password]):
            return Response({
                'status': 'error',
                'message': 'Both email and password are required'
            }, status=status.HTTP_400_BAD_REQUEST)

        db_alias = 'default'

        admin = BrandAdmin.objects.using(db_alias).get(
            email=email, 
            brand_name=brand_name
        )

        if not admin:
            return Response({
                "status": "success",
                "message": "You cannot access the admin panel because you are not an admin."
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not admin.is_active:
            return Response({
                "status": "success",
                "message": "You do not have an active admin account, so you are not able to access it."
            }, status=status.HTTP_400_BAD_REQUEST)
        
        password1 = admin.password
        
        check_pw = bcrypt.checkpw(password.encode(), password1.encode())
        
        if check_pw is True:

            refresh = RefreshToken.for_user(admin)
            
            refresh['brand_name'] = brand_name
            refresh.access_token['brand_name'] = brand_name

            serializer_data = BrandAdminSerializer(admin)
            return Response({
                'status': 'success',
                'message': 'Login successful',
                'data': {
                    'user': serializer_data.data,
                    'tokens': {
                        'refresh': str(refresh),
                        'access': str(refresh.access_token)
                    }
                }
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'status': 'error',
                'message': 'Please enter a valid password'
            }, status=status.HTTP_401_UNAUTHORIZED)


class AdminUsersView(APIValidateView):

    permission_classes = [AdminJWTAuthorization]
    
    def get(self, request):
    
        brand_name = request.brand_name
        users = Users.objects.using(brand_name).filter(brand_name=brand_name)

        serializer_data = AdminUserSerializer(users, many=True)
        return Response({
            "status":"success",
            "data":serializer_data.data
        }, status=status.HTTP_200_OK)


class UpdateUserView(APIValidateView):

    permission_classes = [AdminJWTAuthorization]

    def put(self, request, userid):

        brand_name = request.brand_name

        user = Users.objects.using(brand_name).filter(userid=userid).first()

        serializer_data = AdminUserSerializer(user, data=request.data, partial=True, context={'brand_name':brand_name})
        
        serializer_data.is_valid(raise_exception=True)

        serializer_data.save()

        return Response({
            "status":"success",
            "data":serializer_data.data
        }, status=status.HTTP_200_OK)


class ContactInfoView(APIValidateView):
    
    permission_classes = [AdminJWTAuthorization]

    def get(self, request):
        
        brand_name = request.brand_name

        contacts = ContactUs.objects.using(brand_name).all()

        serializer_data = ContactSerializer(contacts, many=True)

        return Response({
            "status": "success",
            "data" : serializer_data.data
        }, status=status.HTTP_200_OK)
    

class ModifyContactInfo(APIValidateView):

    permission_classes = [AdminJWTAuthorization]

    def put(self, request, contact_id):

        brand_name = request.brand_name

        admin_id = request.admin.id

        contact = ContactUs.objects.using(brand_name).filter(id=contact_id).first()

        if not contact:
            return Response({
                "status": "success",
                "message": "Contact record not found"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if contact.approved_by and contact.approved_by != admin_id:
            return Response({
                "status": "success",
                "message": "Already approved it so not able to modify it"                
            }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer_data = AdminContactSerializer(contact, data=request.data, partial=True, context={'brand_name':brand_name, 'admin_id': admin_id})

        serializer_data.is_valid(raise_exception=True)

        serializer_data.save()

        return Response({
            "status":"success",
            "data": serializer_data.data
        }, status=status.HTTP_200_OK)


class AdminDeleteUserView(APIValidateView):

    permission_classes = [AdminJWTAuthorization]

    def delete(self, request, brand_id, userid):
        
        brand = Brand.objects.using('default').filter(brand_id=brand_id).first()

        user = Users.objects.using(brand.brand_name).filter(userid=userid, brand_name=brand.brand_name).first()

        if not user:
            return Response({
                "status": "success",
                "message": "User not found"
            }, status=status.HTTP_404_NOT_FOUND)
        
        Tasks.objects.using(brand.brand_name).filter(userid=userid).delete()

        user.delete(using=brand.brand_name)

        return Response({
            "status": "success",
            "message": "User deleted successfully"
        }, status=status.HTTP_204_NO_CONTENT)