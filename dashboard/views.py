from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from ..products.models import Product
from ..stores.models import Substore
from django.db.models import Sum, Count

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_dashboard_stats(request):
    try:
        # Get overall stats
        stats = {
            'totalProducts': Product.objects.count(),
            'lowStockProducts': Product.objects.filter(quantity__lte=10).count(),
            'expiringSoonProducts': Product.objects.filter(expiry_date__lte=datetime.now() + timedelta(days=30)).count(),
            'totalStockValue': Product.objects.aggregate(total=Sum('quantity' * 'price'))['total'] or 0,
            'outOfStockCount': Product.objects.filter(quantity=0).count(),
            'lowStockCount': Product.objects.filter(quantity__gt=0, quantity__lte=10).count(),
            'normalStockCount': Product.objects.filter(quantity__gt=10, quantity__lte=50).count(),
            'overstockCount': Product.objects.filter(quantity__gt=50).count(),
        }
        return Response(stats)
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
