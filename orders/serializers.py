from rest_framework import serializers
from django.utils import timezone # For default payment_date
from .models import Order, OrderItem, Payment
from customers.serializers import CustomerSerializer  # For read-only representation
from karigars.serializers import KarigarSerializer    # For read-only representation
from inventory.serializers import FabricSerializer    # For read-only representation
from customers.serializers import MeasurementSerializer # For read-only representation

class OrderItemSerializer(serializers.ModelSerializer):
    # For read operations, to show details instead of just IDs
    fabric_details = FabricSerializer(source='fabric', read_only=True)
    measurement_details = MeasurementSerializer(source='measurement', read_only=True)

    class Meta:
        model = OrderItem
        fields = [
            'id', 'order', 'item_name', 'quantity', 'unit_price',
            'item_specific_instructions', 'fabric', 'fabric_quantity_used_meters',
            'measurement', 'total_item_price', 'created_at', 'updated_at',
            'fabric_details', 'measurement_details'
        ]
        read_only_fields = ['id', 'order', 'total_item_price', 'created_at', 'updated_at']
        # 'fabric' and 'measurement' are writable as PrimaryKeyRelatedField by default
        # if not explicitly specified otherwise.

    def validate(self, data):
        # Example: if fabric is specified, fabric_quantity_used_meters should also be specified.
        if data.get('fabric') and not data.get('fabric_quantity_used_meters'):
            raise serializers.ValidationError({
                "fabric_quantity_used_meters": "Must specify quantity of fabric used if fabric is selected."
            })
        if data.get('fabric_quantity_used_meters', 0) > 0 and not data.get('fabric'):
            raise serializers.ValidationError({
                "fabric": "Cannot specify fabric quantity without selecting a fabric."
            })
        return data


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True) # For nested creation and reading

    # For read-only representation of related objects
    customer_details = CustomerSerializer(source='customer', read_only=True)
    assigned_karigar_details = KarigarSerializer(source='assigned_karigar', read_only=True)

    due_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'customer', 'customer_details', 'order_details', 'status',
            'order_date', 'delivery_due_date', 'completion_date',
            'total_amount', 'advance_payment', 'due_amount',
            'assigned_karigar', 'assigned_karigar_details',
            'voice_note_url', 'design_image_url', 'items',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'order_number', 'due_amount', 'created_at', 'updated_at', 'customer_details', 'assigned_karigar_details']
        # 'customer' and 'assigned_karigar' are writable (ForeignKey)

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError("Order must have at least one item.")
        return value

    def validate(self, data):
        # total_amount should ideally be calculated from items, not taken as direct input
        # unless there's a specific reason for manual override.
        # For now, assuming total_amount might be provided or calculated.
        # If advance_payment is provided, it should not exceed total_amount.
        total_amount = data.get('total_amount')
        advance_payment = data.get('advance_payment', 0)

        if total_amount is not None and advance_payment > total_amount:
            raise serializers.ValidationError({
                "advance_payment": "Advance payment cannot exceed the total order amount."
            })

        # Delivery due date validation
        order_date = data.get('order_date', timezone.now())
        delivery_due_date = data.get('delivery_due_date')
        if delivery_due_date and delivery_due_date < order_date.date():
             raise serializers.ValidationError({'delivery_due_date': 'Delivery due date cannot be before order date.'})

        return data

    def create(self, validated_data):
        items_data = validated_data.pop('items')

        # Calculate total_amount from items if not provided or to verify
        calculated_total_amount = sum(
            item_data.get('quantity', 1) * item_data.get('unit_price', 0) for item_data in items_data
        )

        # If total_amount is part of validated_data, use it, otherwise use calculated.
        # Or, always use calculated_total_amount to ensure consistency.
        # For now, let's prioritize calculated_total_amount for accuracy.
        validated_data['total_amount'] = calculated_total_amount

        order = Order.objects.create(**validated_data)
        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)
            # TODO: Add logic here to deduct fabric_quantity_used_meters from Fabric stock if fabric is linked
        return order

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)

        # Update Order instance fields
        instance.customer = validated_data.get('customer', instance.customer)
        instance.order_details = validated_data.get('order_details', instance.order_details)
        instance.status = validated_data.get('status', instance.status)
        instance.order_date = validated_data.get('order_date', instance.order_date)
        instance.delivery_due_date = validated_data.get('delivery_due_date', instance.delivery_due_date)
        instance.completion_date = validated_data.get('completion_date', instance.completion_date)
        # instance.total_amount = validated_data.get('total_amount', instance.total_amount) # Recalculate if items change
        instance.advance_payment = validated_data.get('advance_payment', instance.advance_payment)
        instance.assigned_karigar = validated_data.get('assigned_karigar', instance.assigned_karigar)
        instance.voice_note_url = validated_data.get('voice_note_url', instance.voice_note_url)
        instance.design_image_url = validated_data.get('design_image_url', instance.design_image_url)

        if items_data is not None:
            # Simple approach: Delete existing items and recreate.
            # More complex: Match by ID, update existing, create new, delete removed.
            # For simplicity in this phase, let's do delete and recreate.
            # This is NOT ideal for production if items have their own lifecycle/status.
            instance.items.all().delete()
            calculated_total_amount = 0
            for item_data in items_data:
                OrderItem.objects.create(order=instance, **item_data)
                calculated_total_amount += item_data.get('quantity', 1) * item_data.get('unit_price', 0)
            instance.total_amount = calculated_total_amount
        else:
            # If items are not part of the update, ensure total_amount is consistent if other fields affect it.
            # Or, if only order fields are updated, total_amount might remain from existing items.
            # For now, if items are not passed, total_amount is not recalculated from items.
            # If total_amount is explicitly in validated_data, it will be set directly.
             instance.total_amount = validated_data.get('total_amount', instance.total_amount)


        instance.save()
        return instance


class PaymentSerializer(serializers.ModelSerializer):
    # order = serializers.PrimaryKeyRelatedField(queryset=Order.objects.all()) # Handled by URL nesting usually

    class Meta:
        model = Payment
        fields = [
            'id', 'order', 'amount_paid', 'payment_date',
            'payment_method', 'notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'order', 'created_at', 'updated_at']
        # 'order' will be set from the URL in the view for nested creation.

    def validate_amount_paid(self, value):
        if value <= 0:
            raise serializers.ValidationError("Payment amount must be positive.")
        return value

    def validate(self, data):
        # Ensure payment_date is not in the future, if not allowing future-dated payments.
        # For now, default is timezone.now, so this check might be redundant unless input is allowed.
        payment_date = data.get('payment_date', timezone.now())
        if payment_date > timezone.now():
            raise serializers.ValidationError({"payment_date": "Payment date cannot be in the future."})

        # Additional validation: Check if total payments exceed order amount
        # This is better done in the view or a signal after payment is associated with an order,
        # as the order instance is needed here.
        # For now, keeping serializer validation focused on its own fields.
        # If self.context['order'] is available (passed from view), we can do:
        # order = self.context.get('order')
        # if order:
        #     current_total_paid = sum(p.amount_paid for p in order.payments.all())
        #     # If updating a payment, exclude its old value from current_total_paid
        #     if self.instance:
        #         current_total_paid -= self.instance.amount_paid
        #     if current_total_paid + data.get('amount_paid', 0) > order.total_amount:
        #         raise serializers.ValidationError("Total payments cannot exceed the order total amount.")
        return data


# Add PaymentSerializer to OrderSerializer for read-only display of payments
class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    payments = PaymentSerializer(many=True, read_only=True) # Display payments related to the order

    customer_details = CustomerSerializer(source='customer', read_only=True)
    assigned_karigar_details = KarigarSerializer(source='assigned_karigar', read_only=True)

    due_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'customer', 'customer_details', 'order_details', 'status',
            'order_date', 'delivery_due_date', 'completion_date',
            'total_amount', 'advance_payment', 'due_amount',
            'assigned_karigar', 'assigned_karigar_details',
            'voice_note', 'design_image', # Changed from _url to actual fields
            'items', 'payments',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'order_number', 'due_amount', 'created_at', 'updated_at',
            'customer_details', 'assigned_karigar_details', 'payments'
        ]
        # 'customer' and 'assigned_karigar' are writable (ForeignKey)

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError("Order must have at least one item.")
        return value

    def validate(self, data):
        total_amount = data.get('total_amount') # This will be recalculated from items in create/update
        advance_payment = data.get('advance_payment', 0)

        # This validation is a bit tricky if total_amount is calculated from items during create/update.
        # The `total_amount` field in `data` here might be the input value, not the calculated one.
        # Better to validate advance_payment against calculated_total_amount in create/update.
        # if total_amount is not None and advance_payment > total_amount:
        #     raise serializers.ValidationError({
        #         "advance_payment": "Advance payment cannot exceed the total order amount."
        #     })

        order_date = data.get('order_date', timezone.now())
        delivery_due_date = data.get('delivery_due_date')
        if delivery_due_date and delivery_due_date < order_date.date():
             raise serializers.ValidationError({'delivery_due_date': 'Delivery due date cannot be before order date.'})

        return data

    def create(self, validated_data):
        items_data = validated_data.pop('items')

        calculated_total_amount = sum(
            item_data.get('quantity', 1) * item_data.get('unit_price', 0) for item_data in items_data
        )
        validated_data['total_amount'] = calculated_total_amount

        # Validate advance_payment against the now calculated_total_amount
        advance_payment = validated_data.get('advance_payment', 0)
        if advance_payment > calculated_total_amount:
            raise serializers.ValidationError({
                 "advance_payment": f"Advance payment ({advance_payment}) cannot exceed the calculated total order amount ({calculated_total_amount})."
            })

        order = Order.objects.create(**validated_data)
        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)
        return order

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)

        instance.customer = validated_data.get('customer', instance.customer)
        instance.order_details = validated_data.get('order_details', instance.order_details)
        instance.status = validated_data.get('status', instance.status)
        instance.order_date = validated_data.get('order_date', instance.order_date)
        instance.delivery_due_date = validated_data.get('delivery_due_date', instance.delivery_due_date)
        instance.completion_date = validated_data.get('completion_date', instance.completion_date)

        new_advance_payment = validated_data.get('advance_payment', instance.advance_payment)

        if items_data is not None:
            instance.items.all().delete()
            calculated_total_amount = 0
            for item_data in items_data:
                OrderItem.objects.create(order=instance, **item_data)
                calculated_total_amount += item_data.get('quantity', 1) * item_data.get('unit_price', 0)
            instance.total_amount = calculated_total_amount
        else:
            # If items are not being updated, total_amount remains as is unless explicitly passed
            instance.total_amount = validated_data.get('total_amount', instance.total_amount)

        if new_advance_payment > instance.total_amount:
            raise serializers.ValidationError({
                "advance_payment": f"Advance payment ({new_advance_payment}) cannot exceed the total order amount ({instance.total_amount})."
            })
        instance.advance_payment = new_advance_payment

        instance.assigned_karigar = validated_data.get('assigned_karigar', instance.assigned_karigar)

        # Handle file fields - they might not be present in every update
        instance.voice_note = validated_data.get('voice_note', instance.voice_note)
        instance.design_image = validated_data.get('design_image', instance.design_image)

        instance.save()
        return instance
