from django.urls import path
from api.views.dashboard import SummaryView, CategoryBreakdownView, MonthlyTrendsView, RecentActivityView

urlpatterns = [
    path("summary/", SummaryView.as_view()),
    path("categories/", CategoryBreakdownView.as_view()),
    path("trends/", MonthlyTrendsView.as_view()),
    path("recent/", RecentActivityView.as_view()),
]
