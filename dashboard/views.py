from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Sum
from datetime import datetime, timedelta
from ..products.models import Product
from ..stores.models import Substore

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_dashboard_stats(request):
    try:
        # Get overall stats
        stats = {
            'totalProducts': Product.objects.count(),
            'lowStockProducts': Product.objects.filter(quantity__lte=10).count(),
            'expiringSoonProducts': Product.objects.filter(expiry_date__lte=datetime.now() + timedelta(days=30)).count(),
            'totalStockValue': Product.objects.aggregate(total=Sum('quantity') * Sum('price'))['total'] or 0,
            'outOfStockCount': Product.objects.filter(quantity=0).count(),
            'lowStockCount': Product.objects.filter(quantity__gt=0, quantity__lte=10).count(),
            'normalStockCount': Product.objects.filter(quantity__gt=10, quantity__lte=50).count(),
            'overstockCount': Product.objects.filter(quantity__gt=50).count(),
        }
        return Response(stats)
    except Exception as e:
        print(f"Dashboard error: {str(e)}")
        return Response(
            {'error': 'Failed to fetch dashboard stats'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_store_specific_stats(request, store_type, store_id):
    try:
        # Example logic, adjust according to your models
        if store_type == 'substore':
            products = Product.objects.filter(substore_id=store_id)
        elif store_type == 'supermarket':
            products = Product.objects.filter(supermarket_id=store_id)
        else:
            return Response({'error': 'Invalid store type'}, status=status.HTTP_400_BAD_REQUEST)

        stats = {
            'totalProducts': products.count(),
            'lowStockProducts': products.filter(quantity__lte=10).count(),
            'expiringSoonProducts': products.filter(
                expiry_date__lte=datetime.now() + timedelta(days=30)
            ).count(),
            'totalStockValue': products.aggregate(
                total=Sum('quantity') * Sum('price')
            )['total'] or 0,
            'outOfStockCount': products.filter(quantity=0).count(),
            'lowStockCount': products.filter(
                quantity__gt=0, quantity__lte=10
            ).count(),
            'normalStockCount': products.filter(
                quantity__gt=10, quantity__lte=50
            ).count(),
            'overstockCount': products.filter(quantity__gt=50).count(),
        }
        return Response(stats)
    except Exception as e:
        print(f"Store stats error: {str(e)}")
        return Response(
            {'error': 'Failed to fetch store stats'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
