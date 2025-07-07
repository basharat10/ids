from rest_framework import serializers
from .models import Customer, Measurement

class MeasurementSerializer(serializers.ModelSerializer):
    # Ensure customer_id is writeable for creating measurements linked to a customer,
    # but not necessarily part of the request body if creating nested.
    # customer = serializers.PrimaryKeyRelatedField(queryset=Customer.objects.all(), required=False)

    class Meta:
        model = Measurement
        fields = ['id', 'customer', 'measurement_set_name', 'measurement_data', 'created_at', 'updated_at']
        read_only_fields = ['id', 'customer', 'created_at', 'updated_at'] # Customer is typically set via URL or nested write

    def validate_measurement_data(self, value):
        if not isinstance(value, dict):
            raise serializers.ValidationError("Measurement data must be a valid JSON object (dict).")
        # Add any specific key validations if necessary, e.g., ensure 'length' or 'chest' exists
        # For now, keeping it flexible.
        return value

class CustomerSerializer(serializers.ModelSerializer):
    measurements = MeasurementSerializer(many=True, read_only=True) # For listing measurements under a customer

    class Meta:
        model = Customer
        fields = ['id', 'name', 'phone_number', 'address', 'measurements', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    # Basic validation for phone number uniqueness is handled by model's unique=True.
    # More complex validation (e.g. format) could be added here if needed.
    def validate_phone_number(self, value):
        # Example: check if phone number contains only digits and possibly a leading +
        # if not re.match(r"^\+?[0-9]{10,15}$", value):
        #     raise serializers.ValidationError("Invalid phone number format.")

        # Check uniqueness, DRF default unique validator handles this based on model field.
        # If updating, ensure it's not conflicting with another existing customer.
        instance = self.instance
        if Customer.objects.filter(phone_number=value).exclude(pk=instance.pk if instance else None).exists():
            raise serializers.ValidationError("This phone number is already registered to another customer.")
        return value

# Serializer for creating/updating measurements directly under a customer (e.g. POST /api/v1/customers/1/measurements/)
class CustomerMeasurementSerializer(serializers.ModelSerializer):
    # customer_id is not needed in request body as it's derived from URL.
    # We will set it in the view.
    class Meta:
        model = Measurement
        fields = ['id', 'measurement_set_name', 'measurement_data', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_measurement_data(self, value):
        if not isinstance(value, dict):
            raise serializers.ValidationError("Measurement data must be a valid JSON object (dict).")
        return value
