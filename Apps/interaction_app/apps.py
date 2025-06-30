from django.apps import AppConfig


class InteractionAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'interaction_app'

    def ready(self):
        import interaction_app.signals