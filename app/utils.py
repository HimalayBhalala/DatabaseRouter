# Include DRF Packages
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class APIValidateView(APIView):
    def handle_exception(self, e):
        return Response({
            'status': 'error',
            'message': f"{str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)