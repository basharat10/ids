from rest_framework import serializers
from .models import Fabric, Accessory

class FabricSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fabric
        fields = [
            'id', 'name', 'color', 'quantity_meters',
            'purchase_price_per_meter', 'supplier',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_quantity_meters(self, value):
        if value < 0:
            raise serializers.ValidationError("Quantity cannot be negative.")
        return value

    # unique_together validation for (name, color) is handled by DRF by default
    # if the constraint is defined in the model's Meta.

class AccessorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Accessory
        fields = [
            'id', 'name', 'type', 'quantity',
            'purchase_price_unit',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_quantity(self, value):
        if value < 0:
            raise serializers.ValidationError("Quantity cannot be negative.")
        return value
