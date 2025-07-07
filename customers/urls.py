from django.urls import path, include
from rest_framework_nested import routers # Using drf-nested-routers for cleaner nested URLs
from .views import CustomerViewSet, MeasurementViewSet

# Main router for top-level resources
router = routers.DefaultRouter()
router.register(r'customers', CustomerViewSet, basename='customer')

# Nested router for measurements under customers
# This will create URLs like:
# /customers/{customer_pk}/measurements/
# /customers/{customer_pk}/measurements/{measurement_pk}/
customers_router = routers.NestedDefaultRouter(router, r'customers', lookup='customer')
customers_router.register(r'measurements', MeasurementViewSet, basename='customer-measurements')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(customers_router.urls)),
]

# Example of what the URLs would look like:
# /api/v1/customers/  (List/Create Customers)
# /api/v1/customers/{id}/ (Retrieve/Update/Delete Customer)
# /api/v1/customers/{customer_id}/measurements/ (List/Create Measurements for a Customer)
# /api/v1/customers/{customer_id}/measurements/{id}/ (Retrieve/Update/Delete Measurement for a Customer)
