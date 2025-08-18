from django.http import JsonResponse

def healthz(request):
    """
    Simple health check endpoint for Kubernetes and other container orchestration systems
    """
    return JsonResponse({"status": "ok"})
