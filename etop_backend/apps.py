from django.apps import AppConfig


class EtopBackendConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "etop_backend"

    def ready(self):
        import etop_backend.signals