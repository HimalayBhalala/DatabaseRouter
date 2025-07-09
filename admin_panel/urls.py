from django.urls import path
from . import views

urlpatterns = [
    path('brands',views.ListOfBrandView.as_view(), name="brand_list"),
    path('register/<brand_id>', views.UserRegistrationView.as_view(), name="admin_register"),
    path('login/<brand_id>',views.AdminLoginView.as_view(), name="admin_login"),
    path("users", views.AdminUsersView.as_view(), name="list-users"),
    path("user/<userid>", views.UpdateUserView.as_view(), name="update_user"),
    path('contacts', views.ContactInfoView.as_view(), name='admin-contacts'),
    path('contact/<contact_id>', views.ModifyContactInfo.as_view(), name='modify-contact')
]