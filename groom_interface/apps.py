from django.apps import AppConfig


class GroomInterfaceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'groom_interface'

    def ready(self):
        import groom_interface.signals  # Ensure signals are loaded
