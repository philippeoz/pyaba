from django.contrib import admin
from apps.api import models


class RegistrationAdmin(admin.ModelAdmin):
    list_display = ("attendee__full_name", "attendee__email", "tutorial__title", "tutorial__event__title")
    search_fields = ("attendee__name", "tutorial__title")
    list_filter = ("tutorial__title", "tutorial__event__title")
    ordering = ("-tutorial__start_datetime", "tutorial__title", "attendee__full_name")


admin.site.register(models.Event)
admin.site.register(models.Tutorial)
admin.site.register(models.Attendee)
admin.site.register(models.Instructor)
admin.site.register(models.Registration, RegistrationAdmin)
