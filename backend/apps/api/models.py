import uuid
import base64

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from django.core.validators import MinValueValidator
from django.core.files.base import ContentFile
from django.utils import timezone
from django.dispatch import receiver
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.template import Template, Context
from django.conf import settings

from apps.api.validators import cpf_validator
from apps.api.utils import html_to_pdf


class Event(models.Model):
    """
    Model representing an event
    """

    title = models.CharField(_("Título"), max_length=255)
    slug = models.SlugField(
        _("Slug"),
        max_length=255,
        help_text=_("Identificador único do evento, usado em URLs"),
        unique=True,
        blank=True,
        null=True,
    )
    image = models.ImageField(_("Imagem"), upload_to="event_images/")
    start_date = models.DateField(_("Data de início"))
    end_date = models.DateField(_("Data de fim"))
    description = models.TextField(_("Descrição"), blank=True, null=True)
    location = models.CharField(
        _("Localização"),
        max_length=255,
        help_text=_("Local onde o evento será realizado"),
        blank=True,
        null=True,
    )
    url = models.URLField(
        _("URL do evento"),
        max_length=255,
        help_text=_("URL do evento para mais informações ou inscrições"),
        blank=True,
        null=True,
    )
    certificate_template = models.FileField(
        _("Modelo de certificado"),
        upload_to="certificate_templates/",
        blank=True,
        null=True,
        help_text=_(
            "Arquivo HTML que será usado como modelo para os certificados emitidos para os tutoriais deste evento"
            " (use as variáveis: {{ attendee_name }}, {{ tutorial_title }}, {{ event_title }}, "
            "{{ event_date }}, {{ event_city }}, {{ hours }})"
        ),
    )

    class Meta:
        verbose_name = _("Evento")
        verbose_name_plural = _("Eventos")

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        """
        Override save method to ensure start_date is before end_date and to generate a slug.
        """
        self.full_clean()
        if self.start_date >= self.end_date:
            raise ValueError(_("A data de início deve ser anterior à data de fim."))
        if not self.slug:
            self.slug = slugify(self.title)
        return super().save(*args, **kwargs)


class CertificateSigner(models.Model):
    """
    Model representing a certificate signer for an event
    """

    name = models.CharField(_("Nome"), max_length=255)
    title = models.CharField(_("Título"), max_length=255)
    signature_image = models.ImageField(
        _("Imagem da Assinatura"),
        upload_to="signatures/",
        blank=True,
        null=True,
        help_text=_("Imagem da assinatura do signatário, usada nos certificados"),
    )

    class Meta:
        verbose_name = _("Signatário do Certificado")
        verbose_name_plural = _("Signatários dos Certificados")

    def __str__(self):
        return f"{self.name} - {self.title}"

    @property
    def signature_image_base64(self):
        """
        Returns the base64 encoded string of the signature image if it exists.
        """
        if self.signature_image:
            with self.signature_image.open("rb") as img_file:
                return f"data:image/png;base64,{base64.b64encode(img_file.read()).decode('utf-8')}"
        return None


class EventCertificateSigner(models.Model):
    """
    Model representing the relationship between an event and its certificate signers
    """

    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name="certificate_signers", verbose_name=_("Evento")
    )
    signer = models.ForeignKey(
        CertificateSigner, on_delete=models.CASCADE, related_name="event_signers", verbose_name=_("Signatário")
    )
    order = models.PositiveIntegerField(
        _("Ordem"),
        default=1,
        help_text=_("Ordem de exibição dos signatários no certificado, começando do 1"),
    )

    class Meta:
        verbose_name = _("Signatário do Certificado do Evento")
        verbose_name_plural = _("Signatários dos Certificados do Evento")
        unique_together = ("event", "signer")

    def __str__(self):
        return f"{self.signer.name} ({self.event.title})"


class Tutorial(models.Model):
    """
    Model representing a tutorial within an event
    """

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="tutorials", verbose_name=_("Evento"))
    title = models.CharField(_("Título"), max_length=255)
    start_datetime = models.DateTimeField(_("Início"))
    end_datetime = models.DateTimeField(_("Fim"))
    vacancies = models.PositiveIntegerField(_("Vagas"), validators=[MinValueValidator(1)])
    duration = models.DurationField(
        _("Duração"), help_text=_("Duração do tutorial em horas, minutos e segundos"), blank=True, null=True
    )
    location = models.CharField(
        _("Localização"),
        max_length=255,
        help_text=_("Local onde o tutorial será realizado"),
        blank=True,
        null=True,
    )
    description = models.TextField(
        _("Descrição"),
        help_text=_("Breve descrição do conteúdo do tutorial"),
        blank=True,
        null=True,
    )
    instructors = models.ManyToManyField(
        "Instructor",
        related_name="tutorials",
        verbose_name=_("Instrutores"),
        blank=True,
        help_text=_("Instrutores que ministrarão o tutorial"),
    )

    class Meta:
        verbose_name = _("Tutorial")
        verbose_name_plural = _("Tutoriais")

    def __str__(self):
        return f"{self.title} ({self.event.title})"

    def save(self, *args, **kwargs):
        """
        Override save method to ensure start_datetime is before end_datetime
        """
        self.full_clean()

        if self.start_datetime >= self.end_datetime:
            raise ValueError(_("A data de início deve ser anterior à data de fim."))

        if self.duration:
            self.end_datetime = self.start_datetime + self.duration

        return super().save(*args, **kwargs)

    def can_subscribe(self, attendee):
        """
        Check if an attendee can be subscribed to the tutorial.
        """
        if self.registrations.filter(attendee=attendee).exists():
            raise ValueError(_("Este participante já está inscrito neste tutorial."))

        if not self.has_slots_available:
            raise ValueError(_("Não há vagas disponíveis para este tutorial."))

        if not attendee.is_available_for(self):
            raise ValueError(_("O participante não está disponível para este tutorial."))

        if self.has_started:
            raise ValueError(_("O tutorial já começou, não é possível inscrever novos participantes."))

        return True

    def subscribe(self, attendee):
        """
        Method to register an attendee for the tutorial
        """
        if not self.can_subscribe(attendee):
            raise ValueError(_("Não é possível inscrever o participante neste tutorial."))

        registration = Registration(tutorial=self, attendee=attendee)
        registration.save()
        return registration

    @property
    def confirmed_registrations(self):
        """
        Returns all confirmed registrations for the tutorial
        """
        return self.registrations.filter(confirmed=True)

    @property
    def has_slots_available(self):
        """
        Check if there are available slots for the tutorial
        """
        return self.confirmed_registrations.count() < self.vacancies

    @property
    def has_started(self):
        """
        Check if the tutorial has started based on the current time.
        """
        return timezone.localtime(timezone.now()) >= timezone.localtime(self.start_datetime)


class Instructor(models.Model):
    """
    Model representing an instructor for a tutorial
    """

    name = models.CharField(_("Nome"), max_length=255)
    bio = models.TextField(_("Biografia"), blank=True, null=True)
    photo = models.ImageField(_("Foto"), upload_to="instructor_photos/", blank=True, null=True)

    class Meta:
        verbose_name = _("Instrutor")
        verbose_name_plural = _("Instrutores")

    def __str__(self):
        return self.name


class Attendee(models.Model):
    """
    Model representing an attendee of a tutorial
    """

    full_name = models.CharField(_("Nome completo"), max_length=255, blank=True, null=True)
    email = models.EmailField(_("E-mail"), blank=True, null=True)
    birthday = models.DateField(_("Data de nascimento"), blank=True, null=True)
    cpf = models.CharField(_("CPF"), max_length=11, unique=True, validators=[cpf_validator])

    class Meta:
        verbose_name = _("Participante")
        verbose_name_plural = _("Participantes")

    def __str__(self):
        return f"{self.full_name} ({self.email})"

    def is_available_for(self, tutorial):
        """
        Check if the attendee is available for the given tutorial
        """
        return not self.registrations.filter(
            tutorial__start_datetime__lt=tutorial.end_datetime, tutorial__end_datetime__gt=tutorial.start_datetime
        ).exists()


class Registration(models.Model):
    """
    Model representing a registration of an attendee for a tutorial
    """

    tutorial = models.ForeignKey(
        Tutorial, on_delete=models.CASCADE, related_name="registrations", verbose_name=_("Tutorial")
    )
    attendee = models.ForeignKey(
        Attendee, on_delete=models.CASCADE, related_name="registrations", verbose_name=_("Participante")
    )
    confirmed = models.BooleanField(_("Confirmado"), default=False)
    registered_at = models.DateTimeField(_("Data de inscrição"), default=timezone.now)
    uuid = models.UUIDField(
        _("UUID"),
        default=uuid.uuid4,
        editable=False,
        unique=True,
        help_text=_("Identificador único da inscrição, usado para certificados e verificações"),
    )
    present = models.BooleanField(
        _("Presente"),
        default=False,
        help_text=_("Indica se o participante esteve presente no tutorial"),
    )
    certificate_pdf = models.FileField(
        _("Certificado PDF"),
        upload_to="certificates/",
        blank=True,
        null=True,
        help_text=_("PDF do certificado emitido para o participante"),
    )

    class Meta:
        verbose_name = _("Inscrição")
        verbose_name_plural = _("Inscrições")
        unique_together = ("tutorial", "attendee")

    def __str__(self):
        return f"{self.attendee.full_name} em {self.tutorial.title}"

    @property
    def certificate_generated(self):
        """
        Check if the certificate has been generated for this registration.
        """
        return self.certificate_pdf is not None and self.certificate_pdf.name != ""

    def render_certificate(self):
        """
        Render the certificate for the registration.
        """
        if not self.tutorial.event.certificate_template:
            raise ValueError(_("O evento não possui um modelo de certificado definido."))

        context = {
            "attendee_name": self.attendee.full_name,
            "tutorial_title": self.tutorial.title,
            "event_title": self.tutorial.event.title,
            "event_date": self.tutorial.start_datetime.strftime("%d/%m/%Y"),
            "event_city": self.tutorial.event.location or _("Localização não definida"),
            "hours": int(self.tutorial.duration.total_seconds() // 3600) if self.tutorial.duration else 0,
            "certificate_signers": self.tutorial.event.certificate_signers.all(),
        }

        with self.tutorial.event.certificate_template.open("r") as template_file:
            template_content = template_file.read()

        return Template(template_content).render(Context(context))

    def generate_certificate(self):
        """
        Generate the PDF certificate for the registration.
        """

        if not self.confirmed:
            raise ValueError(_("O certificado só pode ser gerado para inscrições confirmadas."))
        if not self.present:
            raise ValueError(_("O certificado só pode ser gerado para participantes presentes."))

        pdf_file_content = html_to_pdf(self.render_certificate())
        pdf_file_name = f"{self.uuid}.pdf"
        self.certificate_pdf.save(pdf_file_name, ContentFile(pdf_file_content), save=False)

        # pdf_file_content = html_to_pdf(self.render_certificate())
        # pdf_file_name = f"{self.uuid}.html"
        # self.certificate_pdf.save(pdf_file_name, ContentFile(self.render_certificate()), save=False)

        self.save()


@receiver(models.signals.post_save, sender=Registration)
def send_confirmation_email(sender, instance, created, **kwargs):
    """
    Signal to send a confirmation email after a registration is created.
    """
    if created:
        subject = f"Confirmação de Inscrição no Tutorial: {instance.tutorial.title}"

        html_content = render_to_string(
            "email/tutorial_subscription_confirmation.html",
            {
                "name": instance.attendee.full_name,
                "tutorial_title": instance.tutorial.title,
                "event_title": instance.tutorial.event.title,
                "tutorial_start_date": instance.tutorial.start_datetime.strftime("%d/%m/%Y"),
                "tutorial_date_hour": timezone.localtime(instance.tutorial.start_datetime).strftime("%H:%M"),
                "tutorial_location": instance.tutorial.location,
                "confirmation_link": f"{settings.SITE_URL}/confirmation/{instance.uuid}",
            },
        )

        email = EmailMessage(
            subject=subject, body=html_content, from_email=settings.DEFAULT_FROM_EMAIL, to=[instance.attendee.email]
        )
        email.content_subtype = "html"
        email.send(fail_silently=False)
