import uuid

from django.http import FileResponse, Http404
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.db import transaction

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status

from apps.api.models import Event, Tutorial, Instructor, Registration, Attendee
from apps.api.serializers import EventReadOnlySerializer, TutorialReadOnlySerializer


def event_image(request, pk):
    """
    View that serves the image file for an Event instance.
    """
    try:
        event = Event.objects.get(pk=pk)
    except Event.DoesNotExist:
        raise Http404(_("Event not found"))

    if not event.image:
        raise Http404(_("Event image not found"))

    extension = event.image.name.rsplit(".", 1).pop()
    return FileResponse(
        event.image.open(),
        content_type=f"image/{extension}",
        as_attachment=False,
        filename=f"{event.title}.{extension}",
    )


def instructor_photo(request, pk):
    """
    View that serves the instructor's photo for a Tutorial instance.
    """
    try:
        instructor = Instructor.objects.get(pk=pk)
    except Tutorial.DoesNotExist:
        raise Http404(_("Instructor not found"))

    if not instructor.photo:
        raise Http404(_("Instructor photo not found"))

    extension = instructor.photo.name.rsplit(".", 1).pop()
    return FileResponse(
        instructor.photo.open(),
        content_type=f"image/{extension}",
        as_attachment=False,
        filename=f"{instructor.name}.{extension}",
    )


class EventViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for reading Event instances.
    """

    lookup_field = "slug"
    queryset = Event.objects.all().order_by("-start_date")
    serializer_class = EventReadOnlySerializer

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a single Event instance by slug.
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(
            {
                **serializer.data,
                "tutorials": TutorialReadOnlySerializer(instance.tutorials.all(), many=True).data,
            }
        )


class TutorialViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for Tutorial instances.
    """

    queryset = Tutorial.objects.all()
    serializer_class = TutorialReadOnlySerializer

    @transaction.atomic
    @action(detail=False, methods=["post"])
    def confirm_subscription(self, request):
        """
        Confirm subscription from registration uuid sended via email
        """
        uuid_string = request.data.get("uuid")

        try:
            uuid.UUID(uuid_string)
        except ValueError:
            return Response({"error": _("Invalid UUID")}, status=status.HTTP_400_BAD_REQUEST)

        try:
            registration = Registration.objects.get(uuid=uuid_string)
        except Registration.DoesNotExist:
            return Response({"error": _("Registration not found")}, status=status.HTTP_400_BAD_REQUEST)

        registration.confirmed = True
        registration.save()
        return Response(
            {
                "event_title": registration.tutorial.event.title,
                "event_slug": registration.tutorial.event.slug,
                "tutorial_title": registration.tutorial.title,
            }
        )

    @transaction.atomic
    @action(detail=True, methods=["post"])
    def subscribe(self, request, pk=None):
        """
        Subscribe an attendee to a tutorial.
        """
        cpf = request.data.get("cpf")
        name = request.data.get("name")
        email = request.data.get("email")
        birthday = request.data.get("birthday")

        if not pk or not cpf or len(cpf) != 11 or not cpf.isdigit():
            return Response(
                {"error": _("tutorial_id and correct cpf are required")}, status=status.HTTP_400_BAD_REQUEST
            )

        if birthday:
            try:
                birthday = timezone.datetime.strptime(birthday, "%d/%m/%Y").date()
            except ValueError:
                return Response(
                    {"error": _("Invalid date format for birthday. Use DD/MM/YYYY.")},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        attendee, created = Attendee.objects.get_or_create(cpf=cpf)

        if created and (not name or not email or not birthday):
            raise ValueError(_("Name, email, and birthday are required for new attendees."))

        attendee.full_name = name or attendee.full_name
        attendee.email = email or attendee.email
        attendee.birthday = birthday or attendee.birthday
        attendee.save()

        try:
            tutorial = Tutorial.objects.get(id=pk)
        except Tutorial.DoesNotExist:
            return Response({"error": _("Tutorial with this ID does not exist")}, status=status.HTTP_404_NOT_FOUND)

        try:
            registration = tutorial.subscribe(attendee)
            return Response({"registration_id": registration.id, "subscribed": True})
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @transaction.atomic
    @action(detail=True, methods=["post"])
    def unsubscribe(self, request, pk=None):
        """
        Unsubscribe an attendee from a tutorial.
        """
        cpf = request.data.get("cpf")

        if not pk or not cpf or len(cpf) != 11 or not cpf.isdigit():
            return Response(
                {"error": _("tutorial_id and correct cpf are required")}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            attendee = Attendee.objects.get(cpf=cpf)
        except Attendee.DoesNotExist:
            return Response({"error": _("Attendee with this CPF does not exist")}, status=status.HTTP_404_NOT_FOUND)

        try:
            tutorial = Tutorial.objects.get(id=pk)
        except Tutorial.DoesNotExist:
            return Response({"error": _("Tutorial with this ID does not exist")}, status=status.HTTP_404_NOT_FOUND)

        try:
            registration = tutorial.registrations.get(attendee=attendee)
            registration.delete()
            return Response({"unsubscribed": True})
        except Registration.DoesNotExist:
            return Response(
                {"error": _("Attendee is not subscribed to this tutorial")}, status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=["post"])
    def check_subscription(self, request):
        """
        Check if an attendee is subscribed to a tutorial.
        """
        tutorial_id = request.data.get("tutorial_id")
        cpf = request.data.get("cpf")

        if not tutorial_id or not cpf or len(cpf) != 11 or not cpf.isdigit():
            return Response({"error": _("tutorial_id and cpf are required")}, status=status.HTTP_400_BAD_REQUEST)

        try:
            attendee = Attendee.objects.get(cpf=cpf)
        except Attendee.DoesNotExist:
            return Response({"subscribed": False})

        try:
            tutorial = Tutorial.objects.get(id=tutorial_id)
        except Tutorial.DoesNotExist:
            return Response({"error": _("Tutorial with this ID does not exist")}, status=status.HTTP_404_NOT_FOUND)

        try:
            registration = tutorial.registrations.get(attendee=attendee)
            return Response({"subscribed": registration.confirmed, "registration_id": registration.id})
        except Registration.DoesNotExist:
            return Response({"subscribed": False, "available": attendee.is_available_for(tutorial)})
