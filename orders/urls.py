from django.urls import path, include
# Using DefaultRouter for top-level 'orders' and NestedDefaultRouter for 'payments' under an order.
from rest_framework_nested import routers
from .views import OrderViewSet, PaymentViewSet

# Main router for 'orders'
router = routers.DefaultRouter()
router.register(r'orders', OrderViewSet, basename='order')

# Nested router for 'payments' under 'orders'
# This will create URLs like: /api/v1/orders/{order_pk}/payments/
orders_router = routers.NestedDefaultRouter(router, r'orders', lookup='order')
orders_router.register(r'payments', PaymentViewSet, basename='order-payments')

urlpatterns = [
    path('', include(router.urls)),          # Includes /orders/ and /orders/{id}/
    path('', include(orders_router.urls)),   # Includes /orders/{order_pk}/payments/ and /orders/{order_pk}/payments/{id}/
]

# Example URLs generated:
# GET, POST /api/v1/orders/
# GET, PUT, DELETE /api/v1/orders/{order_id}/
# GET, POST /api/v1/orders/{order_pk}/payments/
# GET, PUT, DELETE /api/v1/orders/{order_pk}/payments/{payment_id}/
