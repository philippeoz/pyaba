"""Management command to close polls for voting."""

from django.core.management.base import BaseCommand

from apps.api import models


class Command(BaseCommand):
    help = "Generate certificates and send emails for attendees of a specific event."

    def add_arguments(self, parser):
        """Add command line arguments for the management command."""

        parser.add_argument("event_slug", type=str, help="Slug of the event to generate certificates for.")
        parser.add_argument(
            "--skip-generation", action="store_true", help="Skip certificate generation if it already exists."
        )
        parser.add_argument("--skip-email", action="store_true", help="Skip sending emails with the certificate.")
        parser.add_argument(
            "--ignore-confirmed",
            action="store_true",
            help="Ignore confirmed registrations.",
        )
        parser.add_argument(
            "--ignore-present",
            action="store_true",
            help="Ignore registrations marked as present.",
        )
        parser.add_argument(
            "--ignore-sent",
            action="store_true",
            help="Ignore registrations that have already sent the certificate email.",
        )

    def handle(self, *args, **options):
        """Handle the command execution logic."""
        self.stdout.write(
            "\n{}{}".format(
                self.style.HTTP_REDIRECT("Generating certificates for the event: "),
                self.style.SUCCESS(options["event_slug"]),
            )
        )
        event = models.Event.objects.get(slug=options["event_slug"])
        tutorials = event.tutorials.all().order_by("title")
        for tutorial in tutorials:
            registrations = tutorial.registrations.all()

            if not options["ignore_confirmed"]:
                registrations = registrations.filter(confirmed=True)
            if not options["ignore_present"]:
                registrations = registrations.filter(present=True)
            if not options["ignore_sent"]:
                registrations = registrations.filter(certificate_sent=False)

            self.stdout.write(
                "\n\n{} ({})\n".format(self.style.HTTP_INFO(tutorial.title), self.style.WARNING(registrations.count()))
            )

            for registration in registrations:
                self.stdout.write(
                    "\n  - {}:".format(self.style.HTTP_INFO(registration.attendee.full_name.strip().upper())), ending=""
                )

                if not options["skip_generation"]:
                    self.stdout.write(" 📄", ending="")
                    try:
                        registration.generate_certificate(
                            check_confirmed=not options["ignore_confirmed"], check_present=not options["ignore_present"]
                        )
                        self.stdout.write("✅", ending="")
                    except Exception as e:
                        self.stdout.write("❌", ending=f" {e}")

                if not options["skip_email"]:
                    self.stdout.write(" 📧", ending="")
                    try:
                        registration.send_certificate_email()
                        self.stdout.write("✅", ending="")
                    except Exception as e:
                        self.stdout.write("❌", ending=f" {e}")

            self.stdout.write("\n")

        self.stdout.write(
            "\n\n{}: {}\n\n".format(
                self.style.SUCCESS("Certificates generated and emails sent successfully!"),
                self.style.HTTP_SUCCESS("All done!"),
            )
        )
