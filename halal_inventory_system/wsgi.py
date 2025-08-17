"""
WSGI config for halal_inventory_system project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os
import sys
import logging

# Configure logging for deployment debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from django.core.wsgi import get_wsgi_application
    
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'halal_inventory_system.settings')
    
    logger.info("Starting WSGI application...")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Python path: {sys.path}")
    
    application = get_wsgi_application()
    logger.info("WSGI application started successfully")
    
except Exception as e:
    logger.error(f"Error starting WSGI application: {str(e)}")
    logger.error(f"Exception type: {type(e).__name__}")
    import traceback
    logger.error(f"Traceback: {traceback.format_exc()}")
    raise
