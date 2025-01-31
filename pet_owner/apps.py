from django.apps import AppConfig


class PetOwnerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'pet_owner'

    def ready(self):
        import pet_owner.signals