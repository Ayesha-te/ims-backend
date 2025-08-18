from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoryViewSet, SupplierViewSet, ProductViewSet,
    StockTransactionViewSet, ExpiryAlertViewSet, 
    ProductTicketViewSet, DashboardViewSet, SupermarketViewSet,
    SubstoreViewSet, POSIntegrationViewSet
)
from .auth_views import (
    register_supermarket, login_supermarket, logout_supermarket,
    get_current_supermarket, refresh_token
)
from .health_views import health_check, api_info, healthz

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'suppliers', SupplierViewSet)
router.register(r'products', ProductViewSet, basename='product')
router.register(r'stock-transactions', StockTransactionViewSet)
router.register(r'expiry-alerts', ExpiryAlertViewSet)
router.register(r'product-tickets', ProductTicketViewSet)
router.register(r'supermarkets', SupermarketViewSet, basename='supermarket')
router.register(r'substores', SubstoreViewSet, basename='substore')

router.register(r'pos-integration', POSIntegrationViewSet, basename='pos-integration')
router.register(r'dashboard', DashboardViewSet, basename='dashboard')

urlpatterns = [
    # Root endpoint for health checks
    path('', health_check, name='health_check'),
    path('health/', health_check, name='health_check_alt'),
    path('healthz/', healthz, name='healthz'),  # ✅ Health check endpoint for Kubernetes
    path('info/', api_info, name='api_info'),
    
    # Authentication endpoints
    path('api/auth/register/', register_supermarket, name='register_supermarket'),
    path('api/auth/login/', login_supermarket, name='login_supermarket'),
    path('api/auth/logout/', logout_supermarket, name='logout_supermarket'),
    path('api/auth/me/', get_current_supermarket, name='current_supermarket'),
    path('api/auth/refresh/', refresh_token, name='refresh_token'),
    
    # API endpoints
    path('api/', include(router.urls)),
    path('api/auth/', include('rest_framework.urls')),
]