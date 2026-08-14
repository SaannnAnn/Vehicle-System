from datetime import date

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models


class Vehicle(models.Model):
    FUEL_TYPE_CHOICES = [
        ("Petrol", "Petrol"),
        ("Diesel", "Diesel"),
        ("Electric", "Electric"),
        ("Hybrid", "Hybrid"),
    ]

    name = models.CharField(max_length=100)
    brand = models.CharField(max_length=100)
    year = models.IntegerField()
    price_per_day = models.DecimalField(max_digits=10, decimal_places=2)
    fuel_type = models.CharField(max_length=20, choices=FUEL_TYPE_CHOICES)
    is_available = models.BooleanField(default=True)

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return f"{self.brand} {self.name} ({self.year})"


phone_validator = RegexValidator(
    regex=r"^\d{10}$",
    message="Phone number must be exactly 10 digits.",
)


class Booking(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name="bookings")
    customer_name = models.CharField(max_length=100)
    customer_phone = models.CharField(max_length=10, validators=[phone_validator])
    start_date = models.DateField()
    end_date = models.DateField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, editable=False)

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return f"Booking #{self.pk} - {self.customer_name} - {self.vehicle}"

    def clean(self):
        errors = {}

        if self.start_date and self.start_date < date.today():
            errors["start_date"] = "Start date cannot be in the past."

        if self.start_date and self.end_date and self.end_date <= self.start_date:
            errors["end_date"] = "End date must be after start date."

        if self.vehicle_id and self.start_date and self.end_date and not errors:
            overlapping = Booking.objects.filter(
                vehicle_id=self.vehicle_id,
                start_date__lt=self.end_date,
                end_date__gt=self.start_date,
            ).exclude(pk=self.pk)
            if overlapping.exists():
                errors["non_field_errors"] = (
                    "This vehicle is already booked for an overlapping date range."
                )

        if errors:
            raise ValidationError(errors)

    def calculate_total_amount(self):
        days = (self.end_date - self.start_date).days
        return days * self.vehicle.price_per_day

    def save(self, *args, **kwargs):
        self.total_amount = self.calculate_total_amount()
        super().save(*args, **kwargs)
