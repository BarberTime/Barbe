from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'empleado'

urlpatterns = [
    path('', views.index, name='index'),
    path('crear/', views.crear, name='crear'),
    path('editar/<uuid:id_empleado>/', views.editar, name='editar'),
    path('eliminar/<uuid:id_empleado>/', views.eliminar, name='eliminar'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
