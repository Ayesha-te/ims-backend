from django.urls import path
from .views import healthz

urlpatterns = [
    path('healthz/', healthz, name='healthz'),  # ✅ Health check endpoint for Kubernetes
]