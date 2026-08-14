from datetime import date, timedelta
from decimal import Decimal

from django.test import TestCase
from rest_framework.exceptions import ValidationError

from .models import Vehicle, Booking
from .serializers import VehicleSerializer, BookingSerializer


class VehicleSerializerTests(TestCase):

    def test_valid_vehicle(self):
        data = {
            "name": "Model 3",
            "brand": "Tesla",
            "year": 2024,
            "price_per_day": "5000.00",
            "fuel_type": "Electric",
            "is_available": True,
        }

        serializer = VehicleSerializer(data=data)

        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_invalid_vehicle_year(self):
        data = {
            "name": "Old Car",
            "brand": "Test",
            "year": 1970,
            "price_per_day": "2000.00",
            "fuel_type": "Petrol",
            "is_available": True,
        }

        serializer = VehicleSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("year", serializer.errors)

    def test_invalid_vehicle_price(self):
        data = {
            "name": "Test Car",
            "brand": "Test",
            "year": 2024,
            "price_per_day": "0.00",
            "fuel_type": "Petrol",
            "is_available": True,
        }

        serializer = VehicleSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("price_per_day", serializer.errors)


class BookingTests(TestCase):

    def setUp(self):
        self.vehicle = Vehicle.objects.create(
            name="Model 3",
            brand="Tesla",
            year=2024,
            price_per_day=Decimal("5000.00"),
            fuel_type="Electric",
            is_available=True,
        )

        self.start_date = date.today() + timedelta(days=5)
        self.end_date = self.start_date + timedelta(days=3)

        self.booking_data = {
            "vehicle": self.vehicle.id,
            "customer_name": "Test Customer",
            "customer_phone": "9876543210",
            "start_date": self.start_date,
            "end_date": self.end_date,
        }

    def test_valid_booking(self):
        serializer = BookingSerializer(data=self.booking_data)

        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_booking_calculates_total_amount(self):
        serializer = BookingSerializer(data=self.booking_data)

        self.assertTrue(serializer.is_valid(), serializer.errors)

        booking = serializer.save()

        self.assertEqual(booking.total_amount, Decimal("15000.00"))

    def test_vehicle_becomes_unavailable_after_booking(self):
        serializer = BookingSerializer(data=self.booking_data)

        self.assertTrue(serializer.is_valid(), serializer.errors)

        serializer.save()

        self.vehicle.refresh_from_db()

        self.assertFalse(self.vehicle.is_available)

    def test_past_start_date_is_rejected(self):
        data = self.booking_data.copy()
        data["start_date"] = date.today() - timedelta(days=1)
        data["end_date"] = date.today() + timedelta(days=2)

        serializer = BookingSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("start_date", serializer.errors)

    def test_end_date_must_be_after_start_date(self):
        data = self.booking_data.copy()
        data["end_date"] = data["start_date"]

        serializer = BookingSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("end_date", serializer.errors)

    def test_invalid_phone_number_is_rejected(self):
        data = self.booking_data.copy()
        data["customer_phone"] = "12345"

        serializer = BookingSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("customer_phone", serializer.errors)

    def test_overlapping_booking_is_rejected(self):
        first_serializer = BookingSerializer(data=self.booking_data)

        self.assertTrue(
            first_serializer.is_valid(),
            first_serializer.errors
        )

        first_serializer.save()

        overlapping_data = {
            "vehicle": self.vehicle.id,
            "customer_name": "Another Customer",
            "customer_phone": "9999999999",
            "start_date": self.start_date + timedelta(days=1),
            "end_date": self.end_date + timedelta(days=2),
        }

        second_serializer = BookingSerializer(data=overlapping_data)

        self.assertFalse(second_serializer.is_valid())
        self.assertIn("vehicle", second_serializer.errors)