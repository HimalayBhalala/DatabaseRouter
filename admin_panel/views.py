# Include Django Packages
from django.shortcuts import render

# Include DjangoRestFrameWork Packages
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

# Include From the Project Folder
from .models import *
from .serializers import *
from app.models import Brand
from .jwt_auth import AdminJWTAuthorization

import bcrypt

# Create your views here.

class ListOfBrandView(APIView):
    def get(self,request):
        try:
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

        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


class UserRegistrationView(APIView):
    def post(self, request, brand_id):
        """
        Register a new user. 
        """
        try:
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

        except Exception as e:
            return Response({
                'status': 'error',
                'message': f'Registration failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AdminLoginView(APIView):
    def post(self, request, brand_id):
        """
        Login user and return JWT tokens.
        
        Request body format:
        {
            "email": "admin@example.com",
            "password": "secure_password"
        }
        """
        try:
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

            try:
                admin = BrandAdmin.objects.using(db_alias).get(
                    email=email, 
                    brand_name=brand_name
                )

                if not admin:
                    return Response({
                        "status": "error",
                        "message": "You cannot access the admin panel because you are not an admin."
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                if not admin.is_active:
                    return Response({
                        "status": "error",
                        "message": "You do not have an active admin account, so you are not able to access it."
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Check password
                password1 = admin.password
                
                #check password is valid or not 
                check_pw = bcrypt.checkpw(password.encode(), password1.encode())
                
                if check_pw is True:
                    # Generate tokens using custom AdminRefreshToken
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
                    
            except Users.DoesNotExist:
                return Response({
                    'status': 'error',
                    'message': 'Invalid credentials'
                }, status=status.HTTP_401_UNAUTHORIZED)

        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class AdminUsersView(APIView):
    permission_classes = [AdminJWTAuthorization]
    
    def get(self, request):
        return Response({
            "success": True,
        })


class UpdateUserView(APIView):
    pass


class ContactUsView(APIView):
    pass