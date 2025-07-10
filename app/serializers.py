from rest_framework import serializers
from .models import Users, Tasks, Brand, ContactUs
from .middleware import get_current_brand

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model
    """
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = Users
        fields = ('userid', 'email', 'firstname', 'surname', 'password', 'brand_name', 'number_task', 'valid_user', 'created_at', 'updated_at')
        read_only_fields = ('userid', 'created_at', 'updated_at', 'brand_name')

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
    class Meta:
        model = Tasks
        fields = (
            'id', 'userid', 'saved_search', 
            'min_price', 'max_price', 'postcode', 'radius', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')

    def validate_saved_search(self, value):
        """Strip whitespace from saved_search"""
        if value:
            return value.strip()
        return value

    def validate_postcode(self, value):
        """Strip whitespace from postcode"""
        if value:
            return value.strip()
        return value

    def create(self, validated_data):
        return Tasks.objects.create(**validated_data)

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
    

class ContactSerializer(serializers.ModelSerializer):
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

    def validate(self, attrs):
        userid = self.context.get('userid')
        brand_name = self.context.get('brand_name')
        request_for_task = attrs.get('request_for_task')

        if not request_for_task or request_for_task == 0 :
            raise ValueError("Please enter a number of tasks you want to create")

        user = Users.objects.using(brand_name).filter(userid=userid, brand_name=brand_name).first()

        if not user:
            raise ValueError("User not found")
        
        if not user.is_active:
            raise ValueError("Your account is deactivated so not able to send a contact us form.")
        
        contacts = ContactUs.objects.using(brand_name).filter(userid=userid)

        print("Total Form count:", contacts.count())
        
        if contacts.exists():
            latest_contact = contacts.latest()
            
            if latest_contact.status == '0':
                raise ValueError("You have already submitted the Contact Us form, and it is currently pending approval by the admin. Please wait for it to be approved before submitting it again.")
        
        attrs['total_count'] = contacts.count() + 1
        attrs['firstname'] = user.firstname
        attrs['surname'] = user.surname
        attrs['email'] = user.email
        attrs['userid'] = userid

        return attrs
    
    def create(self, validated_data):
        brand_name = self.context.get('brand_name')
        return ContactUs.objects.using(brand_name).create(**validated_data)