from rest_framework import serializers
from app.models import *
from .models import *

import bcrypt

class BrandAdminSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = BrandAdmin
        fields = ('email', 'firstname', 'surname', 'password')

    def validate_email(self, value):
        """Strip whitespace from email"""
        if value:
            return value.strip()
        return value

    def validate_firstname(self, value):
        """Strip whitespace from firstname"""
        if value:
            return value.strip()
        return value

    def validate_surname(self, value):
        """Strip whitespace from surname"""
        if value:
            return value.strip()
        return value

    def validate_password(self, value):
        """Strip whitespace from password"""
        if value:
            return value.strip()
        return value

    def validate(self, attrs):
        brand_name = self.context.get('brand_name')
        email = attrs.get('email')
        password = attrs.get('password')
        firstname = attrs.get('firstname')
        surname = attrs.get('surname')

        if not all([email, password, firstname, surname]):
            raise ValueError("All fields (email, password, firstname, surname) are required")

        db_alias = 'default'
        
        existing_user = BrandAdmin.objects.using(db_alias).filter(
            email=email, 
            brand_name=brand_name
        ).first()

        if existing_user:
            raise ValueError('User with this email already exists in this brand')
        
        attrs['brand_name'] = brand_name
        attrs['password'] = bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=15)).decode()

        return attrs
    

    def create(self, validated_data):
        admin = BrandAdmin.objects.create(**validated_data)
        return admin
    

class AdminUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        exclude = ("password", "groups", "user_permissions", "is_staff")

    def validate_email(self, value):
        """Strip whitespace from email"""
        if value:
            return value.strip()
        return value

    def validate_firstname(self, value):
        """Strip whitespace from firstname"""
        if value:
            return value.strip()
        return value

    def validate_surname(self, value):
        """Strip whitespace from surname"""
        if value:
            return value.strip()
        return value

    def validate_brand_name(self, value):
        """Strip whitespace from brand_name"""
        if value:
            return value.strip()
        return value

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save(using=self.context.get('brand_name'))
        return instance
    

class AdminContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactUs
        fields = "__all__"
        read_only_fields = ("userid", "firstname", "surname", "email")

    def validate_description(self, value):
        """Strip whitespace from description"""
        if value:
            return value.strip()
        return value

    def validate_approved_by(self, value):
        """Strip whitespace from approved_by"""
        if value:
            return value.strip()
        return value

    def update(self, instance, validated_data):
        brand_name = self.context.get('brand_name')

        validated_data['approved_by'] = self.context.get('admin_name')

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save(using=self.context.get('brand_name'))
        
        user = Users.objects.using(brand_name).filter(userid=instance.userid, brand_name=brand_name).first()

        if user:
            user.number_task = instance.request_for_task
            user.save(using=brand_name, update_fields=['number_task', 'updated_at'])
        
        return instance