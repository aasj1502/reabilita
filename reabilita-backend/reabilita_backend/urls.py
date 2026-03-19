from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path


def api_root(_request):
    return JsonResponse(
        {
            "name": "Reabilita Backend API",
            "status": "ok",
            "endpoints": {
                "admin": "/admin/",
                "auth": "/api/v1/auth/",
                "pessoal": "/api/v1/pessoal/",
                "saude": "/api/v1/saude/",
                "estatistica": "/api/v1/estatistica/",
            },
        }
    )

urlpatterns = [
    path("", api_root, name="api-root"),
    path("admin/", admin.site.urls),
    path("api/v1/auth/", include("apps.pessoal.auth_urls")),
    path("api/v1/pessoal/", include("apps.pessoal.urls")),
    path("api/v1/saude/", include("apps.saude.urls")),
    path("api/v1/estatistica/", include("apps.estatistica.urls")),
]
