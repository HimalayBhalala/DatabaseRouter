from rest_framework import serializers
from .models import Users, Tasks, Brand
from .middleware import get_current_brand

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model
    """
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = Users
        fields = ('userid', 'email', 'firstname', 'surname', 'password', 'brand_name', 'created_at', 'updated_at')
        read_only_fields = ('userid', 'created_at', 'updated_at', 'brand_name')

    def validate(self, attrs):
        brand_name = self.context.get('brand_name')
        email = attrs.get('email')
        password = attrs.get('password')
        firstname = attrs.get('firstname')
        surname = attrs.get('surname')

        if not all([email, password, firstname, surname]):
            raise ValueError("All fields (email, password, firstname, surname) are required")

        db_alias = brand_name if brand_name != 'default' else 'default'
        
        existing_user = Users.objects.using(db_alias).filter(
            email=email, 
            brand_name=brand_name
        ).first()
        if existing_user:
            raise ValueError('User with this email already exists in this brand')
                    
        return attrs

    def create(self, validated_data):
        validated_data['brand_name'] = get_current_brand()
        user = Users.objects.create_user(**validated_data)
        return user

    def update(self, instance, validated_data):
        if 'password' in validated_data:
            password = validated_data.pop('password')
            instance.set_password(password)
        return super().update(instance, validated_data)

class TaskSerializer(serializers.ModelSerializer):
    """
    Serializer for Task model
    """
    user_email = serializers.EmailField(source='userid.email', read_only=True)
    
    class Meta:
        model = Tasks
        fields = (
            'id', 'userid', 'user_email', 'saved_search', 
            'min_price', 'max_price', 'postcode', 'radius',
            'active', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')

    def create(self, validated_data):
        return super().create(validated_data)

    def validate(self, data):
        """
        Custom validation for price range
        """
        min_price = data.get('min_price')
        max_price = data.get('max_price')
        
        if min_price and max_price and min_price > max_price:
            raise serializers.ValidationError({
                'min_price': 'Minimum price cannot be greater than maximum price'
            })
        
        return data