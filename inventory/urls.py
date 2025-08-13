from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoryViewSet, SupplierViewSet, ProductViewSet,
    StockTransactionViewSet, ExpiryAlertViewSet, 
    ProductTicketViewSet, DashboardViewSet
)

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'suppliers', SupplierViewSet)
router.register(r'products', ProductViewSet)
router.register(r'stock-transactions', StockTransactionViewSet)
router.register(r'expiry-alerts', ExpiryAlertViewSet)
router.register(r'product-tickets', ProductTicketViewSet)
router.register(r'dashboard', DashboardViewSet, basename='dashboard')

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/auth/', include('rest_framework.urls')),
]