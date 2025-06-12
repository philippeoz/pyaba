from django.apps import AppConfig


class ApiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.api"

    def ready(self):
        # Import signals to ensure they are registered
        import apps.api.signals  # noqa
