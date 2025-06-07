from django.db import models
from classes.models import ClassSession

# Create your models here.
class Booking(models.Model):
    session = models.ForeignKey(ClassSession, on_delete=models.CASCADE, related_name='bookings')
    client_name = models.CharField(max_length=100)
    client_email = models.EmailField()
    booked_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-booked_at"]
        # ensure a user doesn’t double‐book the exact same session
        unique_together = [("session", "client_email")]

    def __str__(self):
        return f"{self.client_name} → {self.session}"