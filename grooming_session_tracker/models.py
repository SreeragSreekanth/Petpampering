from django.db import models
from django.contrib.auth import get_user_model
from groom_interface.models import Service, Appointment


User = get_user_model()

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.username}: {self.message[:50]}"

    class Meta:
        ordering = ['-created_at']  # Order notifications by creation time (newest first)



class Invoice(models.Model):
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE,null=True, blank=True)
    total_amount = models.DecimalField(max_digits=6, decimal_places=2,null=True, blank=True)
    status = models.CharField(max_length=20, choices=[('paid', 'Paid'), ('pending', 'Pending')], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Invoice for Appointment {self.appointment.id}"

class Payment(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="payments",null=True, blank=True)
    amount = models.DecimalField(max_digits=6, decimal_places=2,null=True, blank=True)
    paid_by = models.ForeignKey(User, on_delete=models.CASCADE,null=True, blank=True)
    date_paid = models.DateTimeField(auto_now_add=True,null=True, blank=True)

    def __str__(self):
        return f"Payment of {self.amount} for Invoice {self.invoice.id}"

