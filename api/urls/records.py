from django.urls import path
from api.views.records import RecordListView, RecordDetailView

urlpatterns = [
    path("", RecordListView.as_view()),
    path("<int:record_id>/", RecordDetailView.as_view()),
]
