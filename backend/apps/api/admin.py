from django.contrib import admin, messages
from django.utils.translation import gettext_lazy as _

from apps.api import models


@admin.action(description=_("Marcar como presente"))
def attendee_present(modeladmin, request, queryset):
    """
    Mark selected attendees as present.
    """
    count = queryset.update(present=True)
    modeladmin.message_user(
        request,
        _(f"{count} inscrição(ões) marcadas como presente(s)."),
        messages.SUCCESS,
    )


@admin.action(description=_("Marcar como ausente"))
def attendee_absent(modeladmin, request, queryset):
    """
    Mark selected attendees as absent.
    """
    count = queryset.update(present=False)
    modeladmin.message_user(
        request,
        _(f"{count} inscrição(ões) marcadas como ausente(s)."),
        messages.SUCCESS,
    )


class EventCertificateSignerInline(admin.TabularInline):
    model = models.EventCertificateSigner
    extra = 1


class RegistrationAdmin(admin.ModelAdmin):
    list_per_page = 20
    list_display = (
        "attendee__full_name",
        "attendee__email",
        "tutorial__title",
        "tutorial__event__title",
        "confirmed",
        "present",
    )
    search_fields = ("attendee__full_name", "tutorial__title")
    list_filter = ("tutorial__title", "tutorial__event__title", "confirmed", "present")
    ordering = ("-tutorial__start_datetime", "tutorial__title", "attendee__full_name")
    actions = [attendee_present, attendee_absent]
    autocomplete_fields = ("attendee",)


class AttendeeAdmin(admin.ModelAdmin):
    list_display = ("full_name", "email")
    search_fields = ("full_name", "email")
    ordering = ("full_name",)


@admin.register(models.Event)
class EventAdmin(admin.ModelAdmin):
    search_fields = ("title", "slug")
    inlines = [EventCertificateSignerInline]


class TutorialAdmin(admin.ModelAdmin):
    list_display = ("title", "event", "start_datetime", "end_datetime")
    search_fields = ("title", "event__title")
    list_filter = ("event__title",)
    ordering = ("-start_datetime", "title")
    autocomplete_fields = ("event",)


admin.site.register(models.Tutorial, TutorialAdmin)
admin.site.register(models.Attendee, AttendeeAdmin)
admin.site.register(models.Instructor)
admin.site.register(models.CertificateSigner)
admin.site.register(models.Registration, RegistrationAdmin)
