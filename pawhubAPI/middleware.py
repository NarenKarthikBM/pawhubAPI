"""
Custom CORS middleware for PawHub API
This middleware handles CORS requests without requiring django-cors-headers package
"""


class CorsMiddleware:
    """
    Custom CORS middleware to handle Cross-Origin Resource Sharing for Flutter apps
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Handle preflight OPTIONS requests
        if request.method == "OPTIONS":
            response = self._get_cors_response()
        else:
            response = self.get_response(request)

        # Add CORS headers to all responses
        self._add_cors_headers(response, request)
        return response

    def _get_cors_response(self):
        """Create a response for preflight OPTIONS requests"""
        from django.http import HttpResponse

        return HttpResponse()

    def _add_cors_headers(self, response, request):
        """Add CORS headers to the response"""
        # Get origin from request
        origin = request.META.get("HTTP_ORIGIN", "")

        # List of allowed origins for Flutter development
        allowed_origins = [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:8080",
            "http://localhost:62170",
            "http://127.0.0.1:8080",
            "http://10.0.2.2:8000",  # Android emulator
            "http://127.0.0.1:8000",  # iOS simulator
            # Add common Flutter development ports
            "http://localhost:3001",
            "http://localhost:3002",
            "http://localhost:8081",
            "http://localhost:8082",
            "http://localhost:62171",
            "http://localhost:62172",
            # Flutter web development
            "http://localhost:56789",
            "http://127.0.0.1:56789",
            "http://localhost:5000",
            "http://127.0.0.1:5000",
            # Chrome extension / app origins
            "chrome-extension://*",
            "app://*",
        ]

        # Allow all origins in DEBUG mode
        from django.conf import settings

        if getattr(settings, "DEBUG", False):
            response["Access-Control-Allow-Origin"] = "*"
        elif origin in allowed_origins:
            response["Access-Control-Allow-Origin"] = origin
        else:
            # Fallback to allow all origins for development
            response["Access-Control-Allow-Origin"] = "*"

        # Set CORS headers
        response["Access-Control-Allow-Methods"] = (
            "DELETE, GET, OPTIONS, PATCH, POST, PUT"
        )
        response["Access-Control-Allow-Headers"] = (
            "accept, accept-encoding, authorization, device-token, content-type, dnt, "
            "origin, user-agent, x-csrftoken, x-requested-with, "
            "cache-control, x-api-key, x-device-token"
        )
        response["Access-Control-Expose-Headers"] = (
            "content-type, x-api-key, authorization, device-token, x-device-token"
        )
        response["Access-Control-Allow-Credentials"] = "true"
        response["Access-Control-Max-Age"] = "86400"

        return response
