from rest_framework import serializers
from .models import Karigar

class KarigarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Karigar
        fields = ['id', 'name', 'phone_number', 'specializations', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    # Example validation if phone_number was to be unique and not blank
    # def validate_phone_number(self, value):
    #     if value: # Only validate if provided
    #         # Check uniqueness, DRF default unique validator handles this based on model field if unique=True.
    #         # If updating, ensure it's not conflicting with another existing karigar.
    #         instance = self.instance
    #         if Karigar.objects.filter(phone_number=value).exclude(pk=instance.pk if instance else None).exists():
    #             raise serializers.ValidationError("This phone number is already registered to another karigar.")
    #     return value
