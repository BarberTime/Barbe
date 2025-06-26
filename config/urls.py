"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.web import views as web_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', web_views.index, name='index'),
    path('categoria/', include('apps.categoria.urls')),
    path('horario/', include('apps.horario.urls')),
    path('imagen_negocio/', include('apps.imagenes_negocio.urls')),
    path('negocio/', include('apps.negocio.urls')),
    path('pago/', include('apps.pago.urls')),
    path('rol/', include('apps.rol.urls')),
    path('servicio/', include('apps.servicio.urls')),
    path('usuario/', include('apps.usuario.urls', namespace='usuario')),
    path('usuario_rol/', include('apps.usuario_rol.urls')),
    path('suscripcion/', include('apps.suscripcion.urls', namespace='suscripcion')),
    path('empleado/', include('apps.empleado.urls')),
    path('cliente/', include('apps.cliente.urls')),
    path('reserva/', include('apps.reserva.urls', namespace='reserva')),
    path('web/', include('apps.web.urls')),
    path('', include('apps.web.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)