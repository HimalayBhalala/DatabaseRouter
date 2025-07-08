from django.db import transaction, connections
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Users, Brand
from .db_router import get_brand_context, set_brand_context
from .jwt_auth import JWTAuthorization
from .serializers import *

class UserRegistrationView(APIView):
    def post(self, request):
        """
        Register a new user.
        """
        try:
            brand_name = getattr(request, 'brand_name', 'default')
                        
            serializer_data = UserSerializer(data=request.data, context={'brand_name': brand_name})

            serializer_data.is_valid(raise_exception=True)

            user = serializer_data.save()
            # Generate tokens
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'status': 'success',
                'message': 'User registered successfully',
                'data': {
                    'user': {
                        'userid': user.userid,
                        'email': user.email,
                        'firstname': user.firstname,
                        'surname': user.surname,
                        'brand_name': user.brand_name,
                        'database_state': user._state.db
                    },
                    'tokens': {
                        'refresh': str(refresh),
                        'access': str(refresh.access_token)
                    }
                }
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({
                'status': 'error',
                'message': f'Registration failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserLoginView(APIView):
    def post(self, request):
        """
        Login user and return JWT tokens.
        
        Request body format:
        {
            "email": "user@example.com",
            "password": "secure_password"
        }
        """
        try:
            email = request.data.get('email')
            password = request.data.get('password')

            # Validate required fields
            if not all([email, password]):
                return Response({
                    'status': 'error',
                    'message': 'Both email and password are required'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Get current brand context from middleware
            brand_name = get_brand_context()

            # Find user in brand-specific database
            try:
                user = Users.objects.using(brand_name).get(
                    email=email, 
                    brand_name=brand_name
                )
                print(f"User found in {brand_name}: {user.email}")
                
                # Check password
                if user.check_password(password):
                    # Generate tokens
                    refresh = RefreshToken.for_user(user)
                    
                    return Response({
                        'status': 'success',
                        'message': 'Login successful',
                        'data': {
                            'user': {
                                'userid': user.userid,
                                'email': user.email,
                                'firstname': user.firstname,
                                'surname': user.surname,
                                'brand_name': user.brand_name,
                                'database_used': brand_name
                            },
                            'tokens': {
                                'refresh': str(refresh),
                                'access': str(refresh.access_token)
                            }
                        }
                    }, status=status.HTTP_200_OK)
                else:
                    return Response({
                        'status': 'error',
                        'message': 'Invalid credentials'
                    }, status=status.HTTP_401_UNAUTHORIZED)
                    
            except Users.DoesNotExist:
                print(f"User not found in {brand_name} for brand {brand_name}")
                return Response({
                    'status': 'error',
                    'message': 'Invalid credentials'
                }, status=status.HTTP_401_UNAUTHORIZED)

        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CreateTaskAPIView(APIView):
    permission_classes = [JWTAuthorization]

    def post(self, request):
        """
        Create a new task for the authenticated user.
        
        Request body format:
        {
            "saved_search": "string",
            "min_price": float,
            "max_price": float,
            "postcode": "string",
            "radius": integer,
            "active": boolean
        }
        """
        try:
            # Add the user to the data
            data = request.data.copy()
            data['userid'] = request.user.userid

            serializer = TaskSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'status': 'success',
                    'message': 'Task created successfully',
                    'data': serializer.data
                }, status=status.HTTP_201_CREATED)
            
            return Response({
                'status': 'error',
                'message': 'Invalid data provided',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UpdateTaskAPIView(APIView):
    permission_classes = [JWTAuthorization]

    def put(self, request):
        """
        Update an existing task.
        
        Request body format:
        {
            "id": integer,
            "saved_search": "string",
            "min_price": float,
            "max_price": float,
            "postcode": "string",
            "radius": integer,
            "active": boolean
        }
        """
        try:
            task_id = request.data.get('id')
            if not task_id:
                return Response({
                    'status': 'error',
                    'message': 'Task ID is required'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Get current brand context
            brand_name = get_current_brand()

            try:
                task = Tasks.objects.using(brand_name).get(id=task_id, userid=request.user.userid)
            except Tasks.DoesNotExist:
                return Response({
                    'status': 'error',
                    'message': 'Task not found or you do not have permission to update it'
                }, status=status.HTTP_404_NOT_FOUND)

            serializer = TaskSerializer(task, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'status': 'success',
                    'message': 'Task updated successfully',
                    'data': serializer.data
                }, status=status.HTTP_200_OK)
            
            return Response({
                'status': 'error',
                'message': 'Invalid data provided',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DeleteTaskAPIView(APIView):
    permission_classes = [JWTAuthorization]

    def delete(self, request):
        """
        Delete a task.
        
        Request body format:
        {
            "id": integer
        }
        """
        try:
            task_id = request.data.get('id')
            if not task_id:
                return Response({
                    'status': 'error',
                    'message': 'Task ID is required'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Get current brand context
            brand_name = get_current_brand()
            try:
                task = Tasks.objects.using(brand_name).get(id=task_id, userid=request.user.userid)
            except Tasks.DoesNotExist:
                return Response({
                    'status': 'error',
                    'message': 'Task not found or you do not have permission to delete it'
                }, status=status.HTTP_404_NOT_FOUND)

            task.delete()
            return Response({
                'status': 'success',
                'message': 'Task deleted successfully'
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserTasksListView(APIView):
    permission_classes = [JWTAuthorization]

    def get(self, request):
        """
        Get all tasks for the authenticated user.
        
        Query parameters:
        - active: true/false (optional, filter by active status)
        - page: integer (optional, for pagination)
        - limit: integer (optional, number of tasks per page, default 10)
        """
        try:
            # Get current brand context from middleware
            brand_name = get_current_brand()
            
            # Base query - get tasks for current user and brand
            tasks_query = Tasks.objects.using(brand_name).filter(
                userid=request.user.userid
            )
            
            # Filter by active status if provided
            active_filter = request.GET.get('active')
            if active_filter is not None:
                if active_filter.lower() == 'true':
                    tasks_query = tasks_query.filter(active=True)
                elif active_filter.lower() == 'false':
                    tasks_query = tasks_query.filter(active=False)
            
            # Order by creation date (newest first)
            tasks_query = tasks_query.order_by('-created_at')
            
            # Pagination
            page = int(request.GET.get('page', 1))
            limit = int(request.GET.get('limit', 10))
            start = (page - 1) * limit
            end = start + limit
            
            # Get total count for pagination info
            total_tasks = tasks_query.count()
            
            # Get paginated tasks
            tasks = tasks_query[start:end]
            
            # Serialize tasks
            serializer = TaskSerializer(tasks, many=True)
            
            # Calculate pagination info
            total_pages = (total_tasks + limit - 1) // limit
            has_next = page < total_pages
            has_previous = page > 1
            
            return Response({
                'status': 'success',
                'data': {
                    'tasks': serializer.data,
                    'pagination': {
                        'current_page': page,
                        'total_pages': total_pages,
                        'total_tasks': total_tasks,
                        'has_next': has_next,
                        'has_previous': has_previous,
                        'limit': limit
                    },
                    'brand': brand_name
                }
            }, status=status.HTTP_200_OK)
            
        except ValueError as e:
            return Response({
                'status': 'error',
                'message': 'Invalid page or limit parameter'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        