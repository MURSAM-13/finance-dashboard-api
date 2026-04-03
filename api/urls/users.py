from django.urls import path
from api.views.users import UserListView, UserDetailView, UserStatusView

urlpatterns = [
    path("", UserListView.as_view()),
    path("<int:user_id>/", UserDetailView.as_view()),
    path("<int:user_id>/status/", UserStatusView.as_view()),
]
