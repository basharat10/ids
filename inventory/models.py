from django.db import models
from django.utils import timezone

class Fabric(models.Model):
    name = models.CharField(max_length=150, help_text="Fabric Name (e.g., Cotton Latha, Boski)")
    color = models.CharField(max_length=100, blank=True, help_text="Color of the fabric")
    quantity_meters = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, help_text="Quantity in meters")
    purchase_price_per_meter = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text="Cost price (Optional)")
    supplier = models.CharField(max_length=100, blank=True, null=True, help_text="Supplier name (Optional)")
    # last_stocked_date can be auto_now on first creation or manually set.
    # For simplicity, let's make it auto_now_add and allow updates via updated_at or a dedicated stock update view later.
    # last_stocked_date = models.DateField(default=timezone.now, help_text="Date when this fabric was last stocked or its stock was updated")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.color if self.color else 'N/A'}) - {self.quantity_meters}m"

    class Meta:
        ordering = ['name', 'color']
        verbose_name = "Fabric"
        verbose_name_plural = "Fabrics"
        # A specific fabric (e.g., "Cotton Latha" in "Blue") should ideally be a unique entry.
        unique_together = ('name', 'color')


class Accessory(models.Model):
    name = models.CharField(max_length=100, help_text="Accessory Name (e.g., Buttons, Thread Spool, Zipper)")
    # Type could be choices or a ForeignKey to an AccessoryType model for more structure
    type = models.CharField(max_length=50, blank=True, help_text="e.g., Button, Thread, Zipper (Optional)")
    quantity = models.IntegerField(default=0, help_text="Quantity in units (e.g., number of buttons, spools, zippers)")
    purchase_price_unit = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text="Cost price per unit (Optional)")
    # last_stocked_date = models.DateField(default=timezone.now, help_text="Date when this accessory was last stocked or updated")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.type if self.type else 'Generic'}) - {self.quantity} units"

    class Meta:
        ordering = ['name']
        verbose_name = "Accessory"
        verbose_name_plural = "Accessories"
        # Depending on how accessories are managed, name or (name, type) could be unique.
        # For now, allowing multiple entries with same name if type differs or is blank.
        # unique_together = ('name', 'type') # Consider if this makes sense for the business logic
