# Include DRF Packages
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.http import Http404

class APIValidateView(APIView):
    """
    Base view for API validation
    """
    
    def dispatch(self, request, *args, **kwargs):
        """
        Override dispatch to handle database transactions
        """
        try:
            with transaction.atomic():
                return super().dispatch(request, *args, **kwargs)
        except ValueError as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        except Http404 as e:
            return Response({
                'status': 'error',
                'message': 'Resource not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': f'An error occurred: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def strip_whitespace(value):
    """
    Utility function to strip whitespace from string values
    Used in serializer validation methods
    """
    if value and isinstance(value, str):
        return value.strip()
    return value


def validate_string_field(value, field_name=None):
    """
    Enhanced string field validation with strip whitespace
    """
    if value is None:
        return value
    
    if not isinstance(value, str):
        raise ValueError(f"{field_name or 'Field'} must be a string")
    
    # Strip whitespace
    stripped_value = value.strip()
    
    # Check if field is empty after stripping
    if not stripped_value:
        raise ValueError(f"{field_name or 'Field'} cannot be empty or contain only whitespace")
    
    return stripped_value


def validate_email_field(value):
    """
    Enhanced email field validation with strip whitespace
    """
    if value is None:
        return value
    
    stripped_value = strip_whitespace(value)
    
    if not stripped_value:
        raise ValueError("Email cannot be empty or contain only whitespace")
    
    # Basic email validation
    if '@' not in stripped_value:
        raise ValueError("Please enter a valid email address")
    
    return stripped_value.lower()  # Convert to lowercase for consistency