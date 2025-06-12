from django.contrib import admin
from apps.api import models


admin.site.register(models.Event)
admin.site.register(models.Tutorial)
admin.site.register(models.Attendee)
admin.site.register(models.Registration)
admin.site.register(models.Instructor)
