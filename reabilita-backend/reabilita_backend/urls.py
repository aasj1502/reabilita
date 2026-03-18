from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/pessoal/", include("apps.pessoal.urls")),
    path("api/v1/saude/", include("apps.saude.urls")),
    path("api/v1/estatistica/", include("apps.estatistica.urls")),
]
