from django.contrib import admin
from .models import Menu, Booking

# Register your models here.
@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ("title", "price", "inventory")
    search_fields = ("title",)
    list_filter = ("price",)
    ordering = ("title",)
    list_editable = ("price", "inventory")


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("name", "no_of_guests", "booking_date")
    search_fields = ("name",)
    list_filter = ("booking_date",)
    ordering = ("-booking_date",)
    date_hierarchy = "booking_date"