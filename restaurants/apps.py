from django.apps import AppConfig


class RestaurantsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'restaurants'

class YourAppConfig(AppConfig):
    name = 'restaurants'

    def ready(self):
        import restaurants.signals  # Ensure this points to the signals file
