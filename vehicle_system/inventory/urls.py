from django.urls import path

from . import views

urlpatterns = [
    path("vehicles/", views.VehicleListCreateView.as_view(), name="vehicle-list-create"),
    path("vehicles/<int:pk>/", views.VehicleDetailView.as_view(), name="vehicle-detail"),
    path("bookings/", views.BookingListCreateView.as_view(), name="booking-list-create"),
    path("bookings/<int:pk>/", views.BookingDetailView.as_view(), name="booking-detail"),
]
