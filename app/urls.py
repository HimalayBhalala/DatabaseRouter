from django.urls import path
from . import views

urlpatterns = [
    # Authentication URLs
    path('register', views.UserRegistrationView.as_view(), name='register'),
    path('login', views.UserLoginView.as_view(), name='login'),
    
    # Task Management URLs
    path('create-task', views.CreateTaskAPIView.as_view(), name='create-task'),
    path('update-task', views.UpdateTaskAPIView.as_view(), name='update-task'),
    path('delete-task', views.DeleteTaskAPIView.as_view(), name='delete-task'),
    path('my-tasks', views.UserTasksListView.as_view(), name='user-tasks'),
]