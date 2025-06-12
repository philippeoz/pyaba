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
from django.urls import path, re_path, include
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView


# Site name for the admin interface
admin.site.site_header = _("Administração do Portal de Eventos")
admin.site.site_title = _("Portal de Eventos (Admin)")
admin.site.index_title = _("Gerenciamento do Portal de Eventos")
admin.site.site_url = None  # Disable the link to the admin site from the header


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("apps.api.urls")),
    re_path(r"^(?!api/|admin/).*$", TemplateView.as_view(template_name="index.html"), name="spa"),
]
