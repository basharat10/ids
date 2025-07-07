from rest_framework import viewsets, permissions, filters
from .models import Karigar
from .serializers import KarigarSerializer

class KarigarViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Karigars (Craftsmen) to be viewed or edited.
    Supports searching by name, phone_number, and specializations.
    Example: /api/v1/karigars/?search=Ahmed
    """
    queryset = Karigar.objects.all().order_by('name')
    serializer_class = KarigarSerializer
    permission_classes = [permissions.IsAuthenticated] # Ensure only authenticated users can manage karigars

    # Enabling filtering and searching capabilities
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'phone_number', 'specializations'] # Fields to search against with ?search=
    ordering_fields = ['name', 'created_at', 'updated_at']    # Fields available for ?ordering=
    # For more advanced filtering (e.g., filtering by partial specialization match),
    # one might consider adding 'django-filter' and defining a FilterSet class.
    # filterset_fields = ['name', 'specializations'] # Example if using DjangoFilterBackend
