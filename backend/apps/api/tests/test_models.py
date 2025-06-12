import pytest
from datetime import timedelta, date
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError
from model_bakery import baker
from apps.api.models import Event, Tutorial, Attendee, Registration


@pytest.mark.django_db
def test_event_str():
    """Test the string representation of the Event model."""
    event = baker.make(Event, title="My Event")
    assert str(event) == "My Event"


@pytest.mark.django_db
def test_tutorial_str():
    """Test the string representation of the Tutorial model."""
    event = baker.make(Event, title="Event X")
    tutorial = baker.make(Tutorial, event=event, title="Tut X")
    assert str(tutorial) == "Tut X (Event X)"


@pytest.mark.django_db
def test_attendee_str():
    attendee = baker.make(Attendee, full_name="John Doe", email="john@example.com")
    assert str(attendee) == "John Doe (john@example.com)"


@pytest.mark.django_db
def test_registration_str():
    registration = baker.make(Registration)
    expected = f"{registration.attendee.full_name} em {registration.tutorial.title}"
    assert str(registration) == expected


@pytest.mark.django_db
def test_tutorial_save_invalid_dates(event):
    """Test that saving a Tutorial with invalid dates raises a ValueError."""
    now = timezone.now()
    with pytest.raises(ValueError):
        Tutorial.objects.create(
            event=event,
            title="Invalid",
            start_datetime=now,
            end_datetime=now - timedelta(hours=1),
            vacancies=5,
            duration=timedelta(hours=2),
        )


@pytest.mark.django_db
def test_tutorial_save_sets_end_datetime_from_duration():
    """Test that the end_datetime is set correctly based on the duration."""
    event = baker.make(Event)
    start = timezone.now()
    duration = timedelta(hours=3)
    tutorial = Tutorial(
        event=event,
        title="Tut",
        start_datetime=start,
        end_datetime=start + timedelta(hours=1),
        vacancies=10,
        duration=duration,
    )
    tutorial.save()
    assert tutorial.end_datetime == start + duration


@pytest.mark.django_db
def test_event_image_field_accepts_file():
    """Test that the Event model's image field accepts a file."""
    file_content = b"fake image content"
    image = SimpleUploadedFile("test.jpg", file_content, content_type="image/jpeg")
    event = baker.make(Event, image=image)
    event.image.seek(0)  # Reset file pointer to the beginning
    assert file_content == event.image.read()


@pytest.mark.django_db
def test_tutorial_vacancies_validator():
    """Test that the Tutorial model's vacancies field raises an error for zero vacancies."""
    event = baker.make(Event)
    with pytest.raises(Exception):
        Tutorial.objects.create(
            event=event,
            title="No Vacancies",
            start_datetime=timezone.now(),
            end_datetime=timezone.now() + timedelta(hours=1),
            vacancies=0,
            duration=timedelta(hours=1),
        )


@pytest.mark.django_db
def test_registration_unique_together_constraint():
    """Test that the Registration model enforces unique constraints on tutorial and attendee."""
    tutorial = baker.make(Tutorial)
    attendee = baker.make(Attendee, cpf="52998224725")
    baker.make(Registration, tutorial=tutorial, attendee=attendee)
    with pytest.raises(IntegrityError):
        Registration.objects.create(tutorial=tutorial, attendee=attendee)


@pytest.mark.django_db
def test_attendee_is_available_for_no_registrations():
    """Test that an attendee is available for a tutorial if they have no registrations."""
    attendee = baker.make(Attendee)
    tutorial = baker.make(Tutorial)
    assert attendee.is_available_for(tutorial) is True


@pytest.mark.django_db
def test_attendee_is_not_available_for_overlapping(event, tutorial, attendee):
    """Test that an attendee is not available for a tutorial if they have overlapping registrations."""
    tutorial.subscribe(attendee)
    tutorial_2 = baker.make(
        Tutorial,
        event=event,
        start_datetime=tutorial.start_datetime + timedelta(minutes=30),
        end_datetime=tutorial.end_datetime + timedelta(minutes=30),
        vacancies=2,
        duration=timedelta(hours=2),
    )
    assert attendee.is_available_for(tutorial_2) is False


@pytest.mark.django_db
def test_tutorial_subscribe_success():
    """Test that an attendee can successfully subscribe to a tutorial."""
    tutorial = baker.make(Tutorial, vacancies=2)
    attendee = baker.make(Attendee, cpf="52998224725")
    registration = tutorial.subscribe(attendee)
    assert registration.tutorial == tutorial
    assert registration.attendee == attendee
    assert Registration.objects.filter(tutorial=tutorial, attendee=attendee).exists()


@pytest.mark.django_db
def test_tutorial_subscribe_already_registered():
    """Test that an attendee cannot subscribe to a tutorial they are already registered for."""
    tutorial = baker.make(Tutorial, vacancies=2)
    attendee = baker.make(Attendee, cpf="52998224725")
    tutorial.subscribe(attendee)
    with pytest.raises(ValueError, match="já está inscrito"):
        tutorial.subscribe(attendee)


@pytest.mark.django_db
def test_tutorial_subscribe_no_vacancies():
    """Test that an attendee cannot subscribe to a tutorial with no available vacancies."""
    tutorial = baker.make(Tutorial, vacancies=1)
    attendee1 = baker.make(Attendee, cpf="52998224725")
    attendee2 = baker.make(Attendee, cpf="12345678909")
    tutorial.subscribe(attendee1)
    with pytest.raises(ValueError, match="Não há vagas disponíveis"):
        tutorial.subscribe(attendee2)


@pytest.mark.django_db
def test_tutorial_subscribe_attendee_not_available():
    """Test that an attendee cannot subscribe to a tutorial if they are not available due to overlapping schedules."""
    event = baker.make(Event)
    start = timezone.now()
    tutorial1 = baker.make(
        Tutorial,
        event=event,
        start_datetime=start,
        end_datetime=start + timedelta(hours=2),
        vacancies=2,
        duration=timedelta(hours=2),
    )
    tutorial2 = baker.make(
        Tutorial,
        event=event,
        start_datetime=start + timedelta(hours=1),
        end_datetime=start + timedelta(hours=3),
        vacancies=2,
        duration=timedelta(hours=2),
    )
    attendee = baker.make(Attendee, cpf="52998224725")
    tutorial1.subscribe(attendee)
    with pytest.raises(ValueError, match="não está disponível"):
        tutorial2.subscribe(attendee)


@pytest.mark.django_db
def test_attendee_is_available_for():
    """Test that an attendee is available for a tutorial if they have no overlapping registrations."""
    event = baker.make(Event)
    start = timezone.now()
    tutorial1 = baker.make(
        Tutorial,
        event=event,
        start_datetime=start,
        end_datetime=start + timedelta(hours=2),
        vacancies=2,
        duration=timedelta(hours=2),
    )
    tutorial2 = baker.make(
        Tutorial,
        event=event,
        start_datetime=start + timedelta(hours=3),
        end_datetime=start + timedelta(hours=5),
        vacancies=2,
        duration=timedelta(hours=2),
    )
    attendee = baker.make(Attendee, cpf="52998224725")
    tutorial1.subscribe(attendee)
    assert attendee.is_available_for(tutorial2) is True
    # Overlapping tutorial
    tutorial3 = baker.make(
        Tutorial,
        event=event,
        start_datetime=start + timedelta(hours=1),
        end_datetime=start + timedelta(hours=3),
        vacancies=2,
        duration=timedelta(hours=2),
    )
    assert attendee.is_available_for(tutorial3) is False


@pytest.mark.django_db
def test_attendee_cpf_unique_constraint():
    """Test that the Attendee model enforces a unique constraint on the cpf field."""
    baker.make(Attendee, cpf="52998224725")
    with pytest.raises(IntegrityError):
        baker.make(Attendee, cpf="52998224725")
