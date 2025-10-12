import urllib.parse
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import get_user_model
from django.db import close_old_connections

# Get the active user model
User = get_user_model()

@database_sync_to_async
def get_user_from_token(token_key):
    """
    Attempts to retrieve a Django user object from a valid JWT token.
    This function must be synchronous as database operations are by default.
    """
    # Important: Close old database connections before performing a new sync operation
    # This prevents the "SynchronousOnlyOperation" error in ASGI environments.
    close_old_connections() 
    
    try:
        # 1. Validate the token and decode it
        access_token = AccessToken(token_key)
        
        # 2. Extract user ID
        user_id = access_token['user_id']
        
        # 3. Retrieve user from the database
        user = User.objects.get(id=user_id)
        
        # 4. Simple JWT might allow tokens for inactive users; ensure the user is active
        if not user.is_active:
            print(f"JWT Validation: User {user_id} is inactive.")
            return AnonymousUser()
        
        return user
        
    except User.DoesNotExist:
        print("JWT Validation: User ID in token not found in database.")
        return AnonymousUser()
    except Exception as e:
        # Handles exceptions like ExpiredSignatureError, InvalidToken, etc.
        print(f"JWT Validation Error: {e}")
        return AnonymousUser()


class TokenAuthMiddleware:
    """
    Custom middleware that authenticates the user based on a JWT token 
    passed in the WebSocket connection's query string: ?token=<JWT_TOKEN>
    """
    def __init__(self, inner):
        # Store the ASGI application we're wrapping
        self.inner = inner

    async def __call__(self, scope, receive, send):
        # 1. Look for the token in the query string
        try:
            query_string = scope['query_string'].decode()
            query_params = urllib.parse.parse_qs(query_string)
            
            # Extract the token passed under the 'token' key
            token_key = query_params.get('token', [None])[0]
        except Exception:
            token_key = None

        # 2. If a token is found, authenticate the user
        if token_key:
            # Use the asynchronous database function to retrieve the user
            scope['user'] = await get_user_from_token(token_key)
        else:
            # If no token is provided, assign an AnonymousUser
            scope['user'] = AnonymousUser()

        # 3. Pass the enriched scope (with the 'user' object) down to the consumer
        return await self.inner(scope, receive, send)

# Helper function for simpler use in asgi.py
def TokenAuthMiddlewareStack(inner):
    return TokenAuthMiddleware(inner)
