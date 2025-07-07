"""
URL configuration for darziflow_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

urlpatterns = [
    path("admin/", admin.site.urls),

    # API base URL
    path("api/v1/", include([
        # Authentication using SimpleJWT
        path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
        path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
        path('auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'),

        path("accounts/", include("accounts.urls")), # User registration, profiles, logout
        path("", include("customers.urls")), # Includes /customers and nested /customers/{id}/measurements
        path("", include("karigars.urls")),   # Includes /karigars
        path("inventory/", include("inventory.urls")), # Includes /inventory/fabrics and /inventory/accessories
        path("", include("orders.urls")),     # Includes /orders
    ])),

    # Include DRF's browsable API login URLs if DEBUG is True
    # path('api-auth/', include('rest_framework.urls', namespace='rest_framework')), # Optional
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# It's good practice to add a health check endpoint
# from django.http import HttpResponse
# urlpatterns.append(path("health/", lambda r: HttpResponse("OK")))
