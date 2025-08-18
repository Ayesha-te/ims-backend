from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.models import User
from django.conf import settings
from .models import Supermarket

class DevelopmentAuthentication(BaseAuthentication):
    """
    Custom authentication class for development mode.
    Accepts 'dev_demo_token' prefixed tokens and creates a demo user if needed.
    Only active in DEBUG mode.
    """
    
    def authenticate(self, request):
        # Only use this authentication in development mode
        if not settings.DEBUG:
            return None
            
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header.startswith('Bearer '):
            return None
            
        token = auth_header.split(' ')[1]
        
        # Check if it's a development demo token
        if token.startswith('dev_demo_token_'):
            # Get or create a demo user
            user, created = User.objects.get_or_create(
                username='dev_user',
                defaults={
                    'email': 'dev@example.com',
                    'is_active': True,
                    'first_name': 'Development',
                    'last_name': 'User'
                }
            )
            
            # Get or create a demo supermarket
            supermarket, created = Supermarket.objects.get_or_create(
                user=user,
                defaults={
                    'name': 'Development Supermarket',
                    'address': '123 Dev Street',
                    'contact_number': '555-1234',
                    'email': 'dev@example.com',
                    'is_verified': True
                }
            )
            
            print(f"Development authentication successful for token: {token}")
            return (user, token)
            
        return None