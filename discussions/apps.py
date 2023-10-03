from django.apps import AppConfig

default_app_config = 'discussion.apps.DiscussionAppConfig'

class DiscussionsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "discussions"

    def ready(self):
        import discussions.signals
