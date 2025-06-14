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

from apps.api.views import index


admin.site.site_header = _("Gerenciamento de Tutoriais")
admin.site.site_title = _("Pyaba 🐟")
admin.site.index_title = _("Tudo pronto pra mais um evento incrível?")


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("apps.api.urls")),
    re_path(r"^(?!api/|admin/)(?P<slug>[\w-]+)/?$", index, name="spa-event-slug"),
    re_path(r"^(?!api/|admin/).*$", index, name="spa"),
]
