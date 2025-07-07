from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import KarigarViewSet

router = DefaultRouter()
router.register(r'karigars', KarigarViewSet, basename='karigar')

urlpatterns = [
    path('', include(router.urls)),
]

# This will create URLs like:
# /api/v1/karigars/ (List/Create Karigars)
# /api/v1/karigars/{id}/ (Retrieve/Update/Delete Karigar)
