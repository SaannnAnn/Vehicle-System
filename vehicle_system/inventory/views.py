from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics

from .models import Booking, Vehicle
from .serializers import BookingSerializer, VehicleSerializer


class VehicleListCreateView(generics.ListCreateAPIView):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["brand", "fuel_type", "is_available"]


class VehicleDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer


class BookingListCreateView(generics.ListCreateAPIView):
    queryset = Booking.objects.select_related("vehicle").all()
    serializer_class = BookingSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["vehicle", "customer_phone"]


class BookingDetailView(generics.RetrieveAPIView):
    queryset = Booking.objects.select_related("vehicle").all()
    serializer_class = BookingSerializer
