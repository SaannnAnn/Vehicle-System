from datetime import date

from rest_framework import serializers

from .models import Booking, Vehicle


class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = [
            "id",
            "name",
            "brand",
            "year",
            "price_per_day",
            "fuel_type",
            "is_available",
        ]

    def validate_year(self, value):
        current_year = date.today().year
        if value < 1980 or value > current_year + 1:
            raise serializers.ValidationError(
                f"Year must be between 1980 and {current_year + 1}."
            )
        return value

    def validate_price_per_day(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price per day must be greater than zero.")
        return value


class BookingSerializer(serializers.ModelSerializer):
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    vehicle_detail = VehicleSerializer(source="vehicle", read_only=True)

    class Meta:
        model = Booking
        fields = [
            "id",
            "vehicle",
            "vehicle_detail",
            "customer_name",
            "customer_phone",
            "start_date",
            "end_date",
            "total_amount",
        ]

    def validate_customer_phone(self, value):
        if not value.isdigit() or len(value) != 10:
            raise serializers.ValidationError("Phone number must be exactly 10 digits.")
        return value

    def validate(self, attrs):
        # Support partial updates by falling back to existing instance values.
        instance = getattr(self, "instance", None)
        vehicle = attrs.get("vehicle", getattr(instance, "vehicle", None))
        start_date = attrs.get("start_date", getattr(instance, "start_date", None))
        end_date = attrs.get("end_date", getattr(instance, "end_date", None))

        errors = {}

        if start_date and start_date < date.today():
            errors["start_date"] = "Start date cannot be in the past."

        if start_date and end_date and end_date <= start_date:
            errors["end_date"] = "End date must be after start date."

        if not errors and vehicle is not None and not vehicle.is_available:
            # Only block on availability for new bookings; updates to an
            # already-booked vehicle's own booking are still allowed.
            if instance is None or instance.vehicle_id != vehicle.id:
                errors["vehicle"] = "This vehicle is not currently available."

        if not errors and vehicle is not None and start_date and end_date:
            overlapping = Booking.objects.filter(
                vehicle=vehicle,
                start_date__lt=end_date,
                end_date__gt=start_date,
            )
            if instance is not None:
                overlapping = overlapping.exclude(pk=instance.pk)
            if overlapping.exists():
                errors["non_field_errors"] = (
                    "This vehicle is already booked for an overlapping date range."
                )

        if errors:
            raise serializers.ValidationError(errors)

        return attrs

    def create(self, validated_data):
        vehicle = validated_data["vehicle"]
        start_date = validated_data["start_date"]
        end_date = validated_data["end_date"]
        days = (end_date - start_date).days
        validated_data["total_amount"] = days * vehicle.price_per_day

        booking = Booking.objects.create(**validated_data)

        # Business rule: after booking, the vehicle becomes unavailable.
        vehicle.is_available = False
        vehicle.save(update_fields=["is_available"])

        return booking

    def update(self, instance, validated_data):
        vehicle = validated_data.get("vehicle", instance.vehicle)
        start_date = validated_data.get("start_date", instance.start_date)
        end_date = validated_data.get("end_date", instance.end_date)
        days = (end_date - start_date).days
        validated_data["total_amount"] = days * vehicle.price_per_day
        return super().update(instance, validated_data)
