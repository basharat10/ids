import uuid
from django.db import models
from django.conf import settings
from customers.models import Customer, Measurement
from karigars.models import Karigar
from inventory.models import Fabric
from django.utils import timezone
from django.core.exceptions import ValidationError

# Helper function to generate unique order numbers
def generate_order_number():
    timestamp_part = timezone.now().strftime('%Y%m%d')
    # Using first 6 chars of uuid hex for brevity, ensure it's sufficiently unique for daily volume
    random_part = uuid.uuid4().hex[:6].upper()
    return f"DF-{timestamp_part}-{random_part}"

class Order(models.Model):
    ORDER_STATUS_CHOICES = [
        ('Pending', 'Pending'), # Initial state, not yet confirmed by customer or shop
        ('Confirmed', 'Confirmed'), # Customer agreed, shop acknowledged, ready for work
        ('InProgress', 'In Progress'), # Actively being worked on (general status)
        ('Stitching', 'Stitching'), # More specific phase
        ('Finishing', 'Finishing'), # e.g., buttoning, ironing, quality check
        ('ReadyForPickup', 'Ready for Pickup'), # All work done, customer notified
        ('Delivered', 'Delivered'), # Customer received the order
        ('Cancelled', 'Cancelled'), # Order cancelled by customer or shop
        ('OnHold', 'On Hold'), # Work paused for some reason
    ]

    order_number = models.CharField(max_length=50, unique=True, default=generate_order_number, editable=False)
    customer = models.ForeignKey(
        Customer,
        related_name='orders',
        on_delete=models.PROTECT, # Prevent deleting customer if they have orders
        help_text="Customer placing the order"
    )

    order_details = models.TextField(blank=True, null=True, help_text="General notes or special instructions for the entire order")
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='Pending')

    order_date = models.DateTimeField(default=timezone.now, help_text="When the order was placed/recorded")
    delivery_due_date = models.DateField(blank=True, null=True, help_text="Promised delivery date to customer")
    completion_date = models.DateField(blank=True, null=True, help_text="Actual date the order was completed/delivered")

    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Total calculated value of the order (sum of item prices)")
    advance_payment = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Advance amount paid by customer")

    assigned_karigar = models.ForeignKey(
        Karigar,
        related_name='assigned_orders',
        blank=True, null=True,
        on_delete=models.SET_NULL, # If Karigar deleted, order remains but unassigned
        help_text="Karigar primarily responsible for this order"
    )

    # Switched from URLField to FileField for direct upload handling
    voice_note = models.FileField(upload_to='orders/voice_notes/', blank=True, null=True, help_text="Voice note for order instructions")
    design_image = models.ImageField(upload_to='orders/design_images/', blank=True, null=True, help_text="Image sketch or design for the order")
    # Note: For ImageField, Pillow library is required (pip install Pillow)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.order_number} for {self.customer.name} - {self.status}"

    @property
    def due_amount(self):
        return self.total_amount - self.advance_payment

    def clean(self):
        super().clean()
        if self.advance_payment > self.total_amount:
            raise ValidationError({'advance_payment': 'Advance payment cannot exceed total amount.'})
        if self.delivery_due_date and self.delivery_due_date < self.order_date.date():
             raise ValidationError({'delivery_due_date': 'Delivery due date cannot be before order date.'})

    class Meta:
        ordering = ['-order_date', '-created_at']
        verbose_name = "Order"
        verbose_name_plural = "Orders"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    item_name = models.CharField(max_length=255, help_text="e.g., Kameez, Shalwar, Sherwani, Kurta")
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price for this single item")

    item_specific_instructions = models.TextField(blank=True, null=True, help_text="Instructions specific to this item")

    fabric = models.ForeignKey(
        Fabric,
        blank=True, null=True,
        on_delete=models.SET_NULL, # If fabric deleted, item remains but fabric link is lost
        help_text="Fabric from inventory used for this item (Optional)"
    )
    fabric_quantity_used_meters = models.DecimalField(
        max_digits=6, decimal_places=2,
        blank=True, null=True,
        help_text="Meters of fabric used for this item (if applicable from inventory)"
    )

    measurement = models.ForeignKey(
        Measurement,
        blank=True, null=True,
        on_delete=models.SET_NULL, # If measurement deleted, item remains but link lost
        help_text="Specific measurement set for this item (Optional)"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.quantity} x {self.item_name} (Order: {self.order.order_number})"

    @property
    def total_item_price(self):
        return self.quantity * self.unit_price

    def clean(self):
        super().clean()
        if self.quantity <= 0:
            raise ValidationError({'quantity': 'Quantity must be positive.'})
        if self.unit_price < 0:
            raise ValidationError({'unit_price': 'Unit price cannot be negative.'})
        if self.fabric_quantity_used_meters is not None and self.fabric_quantity_used_meters < 0:
            raise ValidationError({'fabric_quantity_used_meters': 'Fabric quantity cannot be negative.'})

    class Meta:
        ordering = ['created_at']
        verbose_name = "Order Item"
        verbose_name_plural = "Order Items"


class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('Cash', 'Cash'),
        ('BankTransfer', 'Bank Transfer'),
        ('Easypaisa', 'Easypaisa'),
        ('JazzCash', 'JazzCash'),
        ('Card', 'Credit/Debit Card'),
        ('Other', 'Other'),
    ]

    order = models.ForeignKey(Order, related_name='payments', on_delete=models.CASCADE, help_text="The order this payment is for")
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, help_text="Amount paid in this transaction")
    payment_date = models.DateTimeField(default=timezone.now, help_text="When the payment was made/recorded")
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='Cash')
    notes = models.TextField(blank=True, null=True, help_text="Optional notes about the payment (e.g., transaction ID, partial payment reason)")

    # recorded_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, help_text="User who recorded this payment")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment of {self.amount_paid} for Order {self.order.order_number} via {self.payment_method}"

    def clean(self):
        super().clean()
        if self.amount_paid <= 0:
            raise ValidationError({'amount_paid': 'Payment amount must be positive.'})
        # Logic to ensure total payments don't exceed order.total_amount + some_buffer can be added here
        # or in the serializer/view to provide better user feedback.
        # For now, basic positive check.

    class Meta:
        ordering = ['-payment_date', '-created_at']
        verbose_name = "Payment"
        verbose_name_plural = "Payments"
