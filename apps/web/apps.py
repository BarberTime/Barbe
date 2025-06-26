from django.apps import AppConfig

class WebConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.web'
    verbose_name = 'Web'
    
    def ready(self):
        super().ready()
        from django.urls import reverse_lazy
        self.namespace = 'web'
