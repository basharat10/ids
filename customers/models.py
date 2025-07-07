from django.db import models

class Customer(models.Model):
    name = models.CharField(max_length=100, help_text="Customer's full name")
    phone_number = models.CharField(max_length=20, unique=True, help_text="Customer's phone number (Unique)")
    address = models.TextField(blank=True, null=True, help_text="Customer's address (Optional)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.phone_number})"

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Customer"
        verbose_name_plural = "Customers"


class Measurement(models.Model):
    customer = models.ForeignKey(Customer, related_name='measurements', on_delete=models.CASCADE)
    measurement_set_name = models.CharField(
        max_length=100,
        help_text="e.g., 'For Kameez Shalwar Jan 2023', 'For Sherwani'"
    )
    # Using JSONField for flexible measurement data.
    # The frontend will be responsible for structuring and presenting this data.
    # Example: {'length': 40, 'chest': 22, 'sleeve': 23.5, 'neck': 15, 'waist': 38 ...}
    measurement_data = models.JSONField(
        help_text="Flexible JSON field for various measurements (e.g., {'length': 40, 'chest': 22})"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.measurement_set_name} for {self.customer.name}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Measurement Set"
        verbose_name_plural = "Measurement Sets"
        # A customer can have multiple measurement sets.
        # A unique_together constraint on (customer, measurement_set_name) could be useful
        # if set names per customer must be unique. For now, not enforcing at DB level.
        # unique_together = ('customer', 'measurement_set_name')
