from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db import transaction
from .models import Supermarket
from .serializers import SupermarketSerializer, SupermarketRegistrationSerializer


@api_view(['POST'])
@permission_classes([AllowAny])
def register_supermarket(request):
    """Register a new supermarket with user account"""
    serializer = SupermarketRegistrationSerializer(data=request.data)
    
    if serializer.is_valid():
        try:
            with transaction.atomic():
                # Create user account
                user = User.objects.create_user(
                    username=serializer.validated_data['email'],
                    email=serializer.validated_data['email'],
                    password=serializer.validated_data['password'],
                    first_name=serializer.validated_data.get('name', '')
                )
                
                # Create supermarket profile
                supermarket = Supermarket.objects.create(
                    user=user,
                    name=serializer.validated_data['name'],
                    address=serializer.validated_data['address'],
                    phone=serializer.validated_data['phone'],
                    email=serializer.validated_data['email'],
                    description=serializer.validated_data.get('description', ''),
                    logo=serializer.validated_data.get('logo', '')
                )
                
                # Generate JWT tokens
                refresh = RefreshToken.for_user(user)
                
                return Response({
                    'message': 'Supermarket registered successfully',
                    'supermarket': SupermarketSerializer(supermarket).data,
                    'user': {
                        'id': user.id,
                        'email': user.email,
                        'first_name': user.first_name,
                    },
                    'access_token': str(refresh.access_token),
                    'refresh_token': str(refresh),
                }, status=status.HTTP_201_CREATED)
                
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_supermarket(request):
    """Login supermarket user"""
    email = request.data.get('email')
    password = request.data.get('password')
    
    if not email or not password:
        return Response({
            'error': 'Email and password are required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Authenticate user
    user = authenticate(username=email, password=password)
    
    if user is None:
        return Response({
            'error': 'Invalid credentials'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    if not user.is_active:
        return Response({
            'error': 'Account is disabled'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        # Get supermarket profile
        supermarket = Supermarket.objects.get(user=user)
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'message': 'Login successful',
            'supermarket': SupermarketSerializer(supermarket).data,
            'user': {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
            },
            'access_token': str(refresh.access_token),
            'refresh_token': str(refresh),
        }, status=status.HTTP_200_OK)
        
    except Supermarket.DoesNotExist:
        # For admin users who might not have supermarket profile
        if user.is_superuser:
            refresh = RefreshToken.for_user(user)
            return Response({
                'message': 'Admin login successful',
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'first_name': user.first_name,
                    'is_admin': True
                },
                'access_token': str(refresh.access_token),
                'refresh_token': str(refresh),
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'error': 'Supermarket profile not found'
            }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_token(request):
    """Refresh access token"""
    refresh_token = request.data.get('refresh_token')
    
    if not refresh_token:
        return Response({
            'error': 'Refresh token is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        refresh = RefreshToken(refresh_token)
        
        return Response({
            'access_token': str(refresh.access_token),
        }, status=status.HTTP_200_OK)
        
    except Exception:
        return Response({
            'error': 'Invalid refresh token'
        }, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
def logout_supermarket(request):
    """Logout supermarket user"""
    refresh_token = request.data.get('refresh_token')
    
    if refresh_token:
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception:
            pass
    
    return Response({
        'message': 'Logout successful'
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_current_supermarket(request):
    """Get current authenticated supermarket details"""
    try:
        supermarket = Supermarket.objects.get(user=request.user)
        return Response({
            'supermarket': SupermarketSerializer(supermarket).data,
            'user': {
                'id': request.user.id,
                'email': request.user.email,
                'first_name': request.user.first_name,
            }
        }, status=status.HTTP_200_OK)
        
    except Supermarket.DoesNotExist:
        if request.user.is_superuser:
            return Response({
                'user': {
                    'id': request.user.id,
                    'email': request.user.email,
                    'first_name': request.user.first_name,
                    'is_admin': True
                }
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'error': 'Supermarket profile not found'
            }, status=status.HTTP_404_NOT_FOUND)