from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FabricViewSet, AccessoryViewSet

router = DefaultRouter()
router.register(r'fabrics', FabricViewSet, basename='fabric')
router.register(r'accessories', AccessoryViewSet, basename='accessory')

urlpatterns = [
    path('', include(router.urls)),
]

# This will create URLs like:
# /api/v1/inventory/fabrics/
# /api/v1/inventory/fabrics/{id}/
# /api/v1/inventory/accessories/
# /api/v1/inventory/accessories/{id}/
