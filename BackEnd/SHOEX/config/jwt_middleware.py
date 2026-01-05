"""
JWT Authentication Middleware for Django GraphQL
Extracts JWT token from Authorization header and authenticates user
"""
import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.utils.functional import SimpleLazyObject

User = get_user_model()


def get_user_from_token(request):
    """
    Extract user from JWT token in Authorization header
    Returns authenticated user or AnonymousUser (never None)
    """
    auth_header = request.META.get('HTTP_AUTHORIZATION', '')
    
    if not auth_header.startswith('Bearer '):
        return AnonymousUser()
    
    token = auth_header.replace('Bearer ', '').strip()
    
    if not token:
        return AnonymousUser()
    
    try:
        # Decode JWT token
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=['HS256']
        )
        
        # Get user ID from payload
        user_id = payload.get('user_id')
        
        if not user_id:
            return AnonymousUser()
        
        # Get user from database
        user = User.objects.get(id=user_id)
        return user
        
    except (jwt.ExpiredSignatureError, jwt.DecodeError, jwt.InvalidTokenError, User.DoesNotExist):
        return AnonymousUser()


class JWTAuthenticationMiddleware:
    """
    Middleware to authenticate user from JWT token
    Only processes requests with Authorization header to avoid conflicts with Django Admin
    """
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Only override user if there's an Authorization header (API requests)
        # This allows Django Admin to use session-based auth
        if 'HTTP_AUTHORIZATION' in request.META:
            request.user = SimpleLazyObject(lambda: get_user_from_token(request))
        
        response = self.get_response(request)
        return response
