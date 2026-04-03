from django.urls import path
from api.views.auth import LoginView, RefreshView, MeView

urlpatterns = [
    path("login/", LoginView.as_view()),
    path("refresh/", RefreshView.as_view()),
    path("me/", MeView.as_view()),
]
