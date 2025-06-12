from django.urls import reverse

from rest_framework import serializers

from apps.api import models


class EventReadOnlySerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = models.Event
        fields = [
            "id",
            "title",
            "image_url",
            "slug",
            "start_date",
            "end_date",
            "description",
            "location",
            "url",
        ]
        read_only_fields = fields

    def get_image_url(self, obj):
        """
        Returns URL to the event image.
        """
        return reverse("event-image", kwargs={"pk": obj.pk})


class InstructorReadOnlySerializer(serializers.ModelSerializer):
    """Serializer for read-only access to Instructor instances."""

    photo_url = serializers.SerializerMethodField()

    class Meta:
        model = models.Instructor
        fields = [
            "id",
            "name",
            "bio",
            "photo_url",
        ]
        read_only_fields = fields

    def get_photo_url(self, obj):
        """
        Returns URL to the instructor's photo.
        """
        if obj.photo:
            return reverse("instructor-photo", kwargs={"pk": obj.pk})
        return None


class TutorialReadOnlySerializer(serializers.ModelSerializer):
    """Serializer for read-only access to Tutorial instances."""

    instructors = InstructorReadOnlySerializer(many=True, read_only=True)
    subscriptions = serializers.IntegerField(source="confirmed_registrations.count", read_only=True)

    class Meta:
        model = models.Tutorial
        fields = [
            "id",
            "event",
            "title",
            "description",
            "start_datetime",
            "end_datetime",
            "vacancies",
            "duration",
            "location",
            "subscriptions",
            "instructors",
        ]
        read_only_fields = fields
