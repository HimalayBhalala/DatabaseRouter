from rest_framework import serializers
from app.models import *

import bcrypt

class BrandAdminSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = BrandAdmin
        fields = ('email', 'firstname', 'surname', 'password')

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