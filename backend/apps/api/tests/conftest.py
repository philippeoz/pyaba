import pytest

from apps.api.models import Attendee, Event, Tutorial


@pytest.fixture
@pytest.mark.django_db
def event():
    # title = models.CharField(_("Título"), max_length=255)
    # image = models.ImageField(_("Imagem"), upload_to="event_images/")
    # start_date = models.DateField(_("Data de início"))
    # end_date = models.DateField(_("Data de fim"))
    # description = models.TextField(_("Descrição"), blank=True, null=True)
    return Event.objects.create(
        title="Test Event",
        start_date="2023-10-01",
        end_date="2023-10-03",
        description="This is a test event.",
    )


@pytest.fixture
@pytest.mark.django_db
def tutorial(event):
    return Tutorial.objects.create(
        event=event,
        title="Test Tutorial",
        start_datetime="2023-10-01T10:00:00Z",
        end_datetime="2023-10-01T12:00:00Z",
        vacancies=10,
        duration="02:00:00",
    )


@pytest.fixture
@pytest.mark.django_db
def attendee():
    # full_name = models.CharField(_("Nome completo"), max_length=255)
    # email = models.EmailField(_("E-mail"))
    # birth_date = models.DateField(_("Data de nascimento"))
    # cpf = models.CharField(_("CPF"), max_length=14, unique=True, validators=[cpf_validator])
    return Attendee.objects.create(
        full_name="John Doe",
        email="jd@gmail.com",
        birth_date="1990-01-01",
        cpf="52998224725",  # Example valid CPF for testing
    )
