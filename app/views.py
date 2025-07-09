# Include DRF Packages
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

# Include From the Project Directory
from .models import Users
from .db_router import get_brand_context
from .jwt_auth import JWTAuthorization
from .serializers import *
from .utils import APIValidateView


class UserRegistrationView(APIValidateView):
    def post(self, request):
        """
        Register a new user.
        """
        brand_name = getattr(request, 'brand_name', 'default')
                    
        serializer_data = UserSerializer(data=request.data, context={'brand_name': brand_name})

        serializer_data.is_valid(raise_exception=True)

        user = serializer_data.save()
        # Generate tokens
        refresh = RefreshToken.for_user(user)

        refresh['brand_name'] = brand_name
        refresh.access_token['brand_name'] = brand_name
        
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


class UserLoginView(APIValidateView):
    def post(self, request):
        """
        Login user and return JWT tokens.
        """
        email = request.data.get('email')
        password = request.data.get('password')

        if not all([email, password]):
            return Response({
                'status': 'error',
                'message': 'Both email and password are required'
            }, status=status.HTTP_400_BAD_REQUEST)

        brand_name = get_brand_context()

        try:
            user = Users.objects.using(brand_name).get(
                email=email, 
                brand_name=brand_name
            )
            
            if user.check_password(password):
                refresh = RefreshToken.for_user(user)
                
                refresh['brand_name'] = brand_name
                refresh.access_token['brand_name'] = brand_name
                
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


class CreateTaskAPIView(APIValidateView):
    permission_classes = [JWTAuthorization]

    def post(self, request):
        """
        Create a new task for the authenticated user.
        """
        data = request.data.copy()
        userid = request.user.userid

        branch_name = request.brand_name

        user = Users.objects.using(branch_name).filter(userid=userid).first()

        if not user.valid_user:
            return Response({
                "status":"error",
                "message": "You have not able to create a Task because invalid user"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        tasks = Tasks.objects.using(branch_name).filter(userid=userid)

        if tasks.count() >= user.number_task:
            return Response({
                "status": "error",
                "message": "You number of task reached so please contact us a admin for increase a task create limit."
            }, status=status.HTTP_400_BAD_REQUEST)
        data['userid'] = userid

        serializer = TaskSerializer(data=data)
        
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response({
            'status': 'success',
            'message': 'Task created successfully',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)


class UpdateTaskAPIView(APIValidateView):
    permission_classes = [JWTAuthorization]

    def put(self, request):
        """
        Update an existing task.
        """
        task_id = request.data.get('id')
        if not task_id:
            return Response({
                'status': 'error',
                'message': 'Task ID is required'
            }, status=status.HTTP_400_BAD_REQUEST)

        brand_name = request.brand_name

        try:
            task = Tasks.objects.using(brand_name).get(id=task_id, userid=request.user.userid)
        except Tasks.DoesNotExist:
            return Response({
                'status': 'error',
                'message': 'Task not found or you do not have permission to update it'
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = TaskSerializer(task, data=request.data, partial=True)
        
        serializer.is_valid(raise_exception=True)
       
        serializer.save()

        return Response({
            'status': 'success',
            'message': 'Task updated successfully',
            'data': serializer.data
        }, status=status.HTTP_200_OK)


class DeleteTaskAPIView(APIValidateView):
    permission_classes = [JWTAuthorization]

    def delete(self, request):
        """
        Delete a task.
        """
        task_id = request.data.get('id')
        if not task_id:
            return Response({
                'status': 'error',
                'message': 'Task ID is required'
            }, status=status.HTTP_400_BAD_REQUEST)

        brand_name = request.brand_name
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


class UserTasksListView(APIValidateView):
    permission_classes = [JWTAuthorization]

    def get(self, request):
        """
        Get all tasks for the authenticated user.
        """
        brand_name = request.brand_name
        
        tasks_query = Tasks.objects.using(brand_name).filter(
            userid=request.user.userid
        )
        
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
        
    
class ContactUsView(APIValidateView):

    permission_classes = [JWTAuthorization]

    def post(self, request):
 
        userid = request.user.userid

        brand_name = request.brand_name
        serializer_data = ContactSerializer(data=request.data, context={'userid': userid , 'brand_name': brand_name})
        
        serializer_data.is_valid(raise_exception=True)

        serializer_data.save()

        return Response({
            "status": "success",
            "message": "Contact Us form submitted successfully"
        }, status=status.HTTP_201_CREATED)