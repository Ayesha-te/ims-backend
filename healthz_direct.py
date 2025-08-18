from django.http import JsonResponse
from django.urls import path

def healthz(request):
    """
    Simple health check endpoint for Kubernetes and other container orchestration systems
    """
    return JsonResponse({"status": "ok"})

urlpatterns = [
    path('healthz/', healthz, name='healthz'),
]