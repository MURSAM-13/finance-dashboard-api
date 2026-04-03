from django.urls import path, include

urlpatterns = [
    path("auth/", include("api.urls.auth")),
    path("users/", include("api.urls.users")),
    path("records/", include("api.urls.records")),
    path("dashboard/", include("api.urls.dashboard")),
]
