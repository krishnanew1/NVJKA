from django.apps import AppConfig


class UsersConfig(AppConfig):
    name = 'users'
    default_auto_field = 'django.db.models.BigAutoField'
    
    def ready(self):
        """
        Import signal handlers when the app is ready.
        This ensures signals are registered and will be triggered.
        """
        import users.signals  # noqa: F401
