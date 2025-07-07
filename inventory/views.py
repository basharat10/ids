from rest_framework import viewsets, permissions, filters
from .models import Fabric, Accessory
from .serializers import FabricSerializer, AccessorySerializer

class FabricViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Fabrics to be viewed or edited.
    Supports searching by name, color, and supplier.
    Example: /api/v1/inventory/fabrics/?search=Cotton
    """
    queryset = Fabric.objects.all().order_by('name', 'color')
    serializer_class = FabricSerializer
    permission_classes = [permissions.IsAuthenticated] # Ensure only authenticated users can manage fabrics

    # Enabling filtering and searching
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'color', 'supplier'] # Fields for ?search=
    ordering_fields = ['name', 'color', 'quantity_meters', 'updated_at', 'created_at'] # Fields for ?ordering=
    # For more advanced filtering (e.g. range filters for quantity),
    # consider 'django-filter' and define a FilterSet.
    # filterset_fields = ['name', 'color', 'supplier'] # Example if using DjangoFilterBackend

class AccessoryViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Accessories to be viewed or edited.
    Supports searching by name and type.
    Example: /api/v1/inventory/accessories/?search=Button
    """
    queryset = Accessory.objects.all().order_by('name')
    serializer_class = AccessorySerializer
    permission_classes = [permissions.IsAuthenticated] # Ensure only authenticated users can manage accessories

    # Enabling filtering and searching
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'type'] # Fields for ?search=
    ordering_fields = ['name', 'type', 'quantity', 'updated_at', 'created_at'] # Fields for ?ordering=
    # filterset_fields = ['name', 'type'] # Example if using DjangoFilterBackend
