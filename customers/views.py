from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Customer, Measurement
from .serializers import CustomerSerializer, MeasurementSerializer, CustomerMeasurementSerializer

class CustomerViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows customers to be viewed or edited.
    Supports searching by name and phone_number.
    Example: /api/v1/customers/?search=John
    """
    queryset = Customer.objects.all().prefetch_related('measurements').order_by('-created_at')
    serializer_class = CustomerSerializer
    permission_classes = [permissions.IsAuthenticated] # Only authenticated users can manage customers

    # Enabling filtering and searching
    filter_backends = [filters.SearchFilter, filters.OrderingFilter] # DjangoFilterBackend can be added for more complex filters
    search_fields = ['name', 'phone_number', 'address'] # For ?search=...
    ordering_fields = ['name', 'created_at', 'updated_at'] # For ?ordering=...
    # filterset_fields = ['name', 'phone_number'] # If using DjangoFilterBackend

    # Example of a custom action (though not strictly needed for basic CRUD)
    # @action(detail=True, methods=['get'], url_path='all-measurements')
    # def list_customer_measurements(self, request, pk=None):
    #     customer = self.get_object()
    #     measurements = customer.measurements.all()
    #     serializer = MeasurementSerializer(measurements, many=True, context={'request': request})
    #     return Response(serializer.data)

class MeasurementViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows measurements for a specific customer to be viewed or edited.
    This ViewSet is intended to be used nested under a customer.
    e.g., /api/v1/customers/{customer_pk}/measurements/
    """
    queryset = Measurement.objects.all() # Base queryset, will be filtered
    serializer_class = CustomerMeasurementSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['measurement_set_name', 'measurement_data']
    ordering_fields = ['measurement_set_name', 'created_at']


    def get_queryset(self):
        """
        This view should only return measurements for the customer
        specified in the URL.
        """
        customer_pk = self.kwargs.get('customer_pk')
        if not customer_pk:
            # This case should ideally not be reached if routes are set up for nesting only
            return Measurement.objects.none()

        # Ensure the customer exists
        get_object_or_404(Customer, pk=customer_pk)
        return Measurement.objects.filter(customer_id=customer_pk).order_by('-created_at')

    def perform_create(self, serializer):
        """
        Link the measurement to the customer from the URL.
        """
        customer_pk = self.kwargs.get('customer_pk')
        customer = get_object_or_404(Customer, pk=customer_pk)
        serializer.save(customer=customer)

    # get_serializer_class can be used if different serializers are needed for different actions
    # def get_serializer_class(self):
    #     if self.action == 'list' or self.action == 'retrieve':
    #         return CustomerMeasurementDetailSerializer # A potentially more detailed serializer
    #     return CustomerMeasurementSerializer
