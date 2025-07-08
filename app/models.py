from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone


    

class Brand(models.Model):
    """Model to manage different brands/tenants"""
    brand_id = models.AutoField(primary_key=True)
    brand_name = models.CharField(max_length=100, unique=True)
    database_name = models.CharField(max_length=100, unique=True)
    subdomain = models.CharField(max_length=100, unique=True, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Database configuration for this brand
    db_host = models.CharField(max_length=255, default='localhost')
    db_port = models.CharField(max_length=10, default='3306')
    db_user = models.CharField(max_length=100)

    def __str__(self):
        return self.brand_name

    class Meta:
        db_table = 'brands'


    @property
    def id(self):
        """ For getting a brand ID"""
        return self.brand_id


class BrandAdmin(models.Model):
    """Include a Brand wise admin"""
    firstname = models.CharField(max_length=50)
    surname = models.CharField(max_length=50)
    email = models.CharField(max_length=50, unique=False)
    password = models.CharField(max_length=255)
    brand_name = models.CharField(max_length=100, db_index=True)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

class Users(AbstractBaseUser, PermissionsMixin):
    userid = models.AutoField(primary_key=True)
    firstname = models.CharField(max_length=50)
    surname = models.CharField(max_length=50)
    email = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=255)
    brand_name = models.CharField(max_length=100, db_index=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    number_task = models.IntegerField(default=0)
    valid_user = models.BooleanField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['firstname', 'surname', 'brand_name']

    @property
    def id(self):
        """Map id to userid for JWT token compatibility"""
        return self.userid

    def __str__(self):
        return f"{self.email} ({self.brand_name})"

    class Meta:
        db_table = 'users'
        unique_together = [['email', 'brand_name']]

class Tasks(models.Model):
    userid = models.ForeignKey(Users, on_delete=models.CASCADE, db_column='userid')
    saved_search = models.CharField(max_length=200)
    min_price = models.FloatField(blank=True, null=True)
    max_price = models.FloatField(blank=True, null=True)
    postcode = models.CharField(max_length=100, blank=True, null=True)
    radius = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'tasks'
        unique_together = [['userid', 'saved_search']]
