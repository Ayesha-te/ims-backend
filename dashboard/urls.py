from django.urls import path
from . import views

urlpatterns = [
    path('stats/', views.get_dashboard_stats, name='dashboard-stats'),
    path('<str:store_type>/<str:store_id>/stats/', 
         views.get_store_specific_stats, 
         name='store-stats'),
]
