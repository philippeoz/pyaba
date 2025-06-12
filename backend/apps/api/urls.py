from django.urls import path
from rest_framework import routers

from apps.api.views import EventViewSet, TutorialViewSet, event_image, instructor_photo

router = routers.DefaultRouter()
router.register(r"events", EventViewSet, basename="events")
router.register(r"tutorials", TutorialViewSet, basename="tutorials")
urlpatterns = [
    path("events/<int:pk>/image/", event_image, name="event-image"),
    path("instructors/<int:pk>/photo/", instructor_photo, name="instructor-photo"),
] + router.urls
