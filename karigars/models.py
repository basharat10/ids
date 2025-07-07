from django.db import models

class Karigar(models.Model):
    name = models.CharField(max_length=100, help_text="Karigar's full name")
    phone_number = models.CharField(max_length=20, blank=True, null=True, help_text="Karigar's phone number (Optional, but recommended)")
    # Consider making phone_number unique if it's a primary identifier for them.
    # unique=True if phone_number else False - this logic needs careful handling if some are blank.
    # For now, not making it unique to allow flexibility.
    specializations = models.TextField(blank=True, null=True, help_text="e.g., Shalwar Kameez specialist, Sherwani expert (Optional)")
    # Future fields could include: is_active, rating, notes, address, etc.
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name'] # Order by name by default
        verbose_name = "Karigar (Craftsman)"
        verbose_name_plural = "Karigars (Craftsmen)"
