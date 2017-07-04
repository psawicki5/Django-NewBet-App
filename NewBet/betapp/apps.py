from django.apps import AppConfig


class BetappConfig(AppConfig):
    name = 'betapp'

    def ready(self):
        import betapp.signals