from django.apps import AppConfig


class UsersConfig(AppConfig):
    name = 'apps.users'
    default_auto_field = 'django.db.models.BigAutoField'
    
    def ready(self):
        """
        Import signal handlers when the app is ready.
        This ensures signals are registered and will be triggered.
        """
        import apps.users.signals  # noqa: F401
