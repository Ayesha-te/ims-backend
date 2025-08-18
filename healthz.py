from django.http import JsonResponse

def healthz_view(request):
    """
    Simple health check endpoint for Kubernetes and other container orchestration systems
    """
    return JsonResponse({"status": "ok"})