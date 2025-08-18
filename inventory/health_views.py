from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from django.conf import settings
import django

@api_view(['GET', 'HEAD'])
@permission_classes([AllowAny])
def health_check(request):
    """
    Health check endpoint for monitoring services
    """
    if request.method == 'HEAD':
        # Return minimal response for HEAD requests
        return JsonResponse({}, status=200)
    
    return Response({
        'status': 'healthy',
        'message': 'Halal Inventory Management System is running',
        'version': '1.0.0',
        'django_version': django.get_version(),
        'debug': settings.DEBUG
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([AllowAny])
def healthz(request):
    """
    Simple health check endpoint for Kubernetes and other container orchestration systems
    """
    return JsonResponse({"status": "ok"})

@api_view(['GET'])
@permission_classes([AllowAny])
def api_info(request):
    """
    API information endpoint
    """
    return Response({
        'name': 'Halal Inventory Management System API',
        'version': '1.0.0',
        'endpoints': {
            'health': '/health/',
            'healthz': '/healthz/',
            'admin': '/admin/',
            'api': {
                'products': '/api/products/',
                'categories': '/api/categories/',
                'suppliers': '/api/suppliers/',
                'stock_alerts': '/api/stock-alerts/',
                'import': {
                    'excel': '/api/products/import-excel/',
                    'image': '/api/products/import-image/'
                }
            },
            'auth': '/auth/token/'
        }
    }, status=status.HTTP_200_OK)