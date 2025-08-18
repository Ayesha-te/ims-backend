from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
import base64
import os
import json
import uuid
from datetime import datetime
from .models import Product, Supermarket, Substore

@api_view(['POST'])
@permission_classes([IsAuthenticated])  # Require authentication
def import_excel(request):
    """
    Import products from Excel file
    """
    # Log authentication info for debugging
    print(f"User: {request.user}")
    print(f"Authenticated: {request.user.is_authenticated}")
    print(f"Auth header: {request.META.get('HTTP_AUTHORIZATION', 'None')}")
    try:
        # Get data from request
        file_name = request.data.get('file_name')
        file_data = request.data.get('file_data')
        target_stores = request.data.get('target_stores', [])
        add_to_all_stores = request.data.get('add_to_all_stores', False)
        
        # Log the request for debugging
        print(f"Received import request for file: {file_name}")
        print(f"Target stores: {target_stores}")
        print(f"Add to all stores: {add_to_all_stores}")
        
        # In a real implementation, we would:
        # 1. Decode the base64 file data
        # 2. Save it to a temporary file
        # 3. Process the Excel file
        # 4. Create products in the database
        
        # For now, just return a success response
        return Response({
            'status': 'success',
            'message': 'Excel import initiated',
            'id': str(uuid.uuid4()),
            'file_name': file_name,
            'timestamp': datetime.now().isoformat()
        }, status=status.HTTP_202_ACCEPTED)
        
    except Exception as e:
        print(f"Error in import_excel: {str(e)}")
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])  # Require authentication
def import_image(request):
    """
    Import products from image (OCR)
    """
    # Log authentication info for debugging
    print(f"User: {request.user}")
    print(f"Authenticated: {request.user.is_authenticated}")
    print(f"Auth header: {request.META.get('HTTP_AUTHORIZATION', 'None')}")
    try:
        # Get data from request
        image_name = request.data.get('image_name')
        image_data = request.data.get('image_data')
        target_stores = request.data.get('target_stores', [])
        add_to_all_stores = request.data.get('add_to_all_stores', False)
        
        # Log the request for debugging
        print(f"Received image import request for: {image_name}")
        print(f"Target stores: {target_stores}")
        print(f"Add to all stores: {add_to_all_stores}")
        
        # In a real implementation, we would:
        # 1. Decode the base64 image data
        # 2. Save it to a temporary file
        # 3. Process the image with OCR
        # 4. Extract product information
        # 5. Return the extracted data
        
        # For now, just return a mock response with some extracted data
        return Response({
            'status': 'success',
            'message': 'Image processed successfully',
            'id': str(uuid.uuid4()),
            'image_name': image_name,
            'timestamp': datetime.now().isoformat(),
            'extracted_data': {
                'name': 'Sample Product',
                'barcode': '123456789012',
                'price': 9.99,
                'quantity': 10,
                'category': 'Food',
                'halal_certified': True
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        print(f"Error in import_image: {str(e)}")
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)