from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth
from rest_framework.views import APIView
from rest_framework.response import Response
from api.models import FinancialRecord
from api.permissions import IsViewerOrAbove, IsAnalystOrAbove


def active_records():
    return FinancialRecord.objects.filter(deleted_at__isnull=True)


class SummaryView(APIView):
    permission_classes = [IsViewerOrAbove]

    def get(self, request):
        totals = (
            active_records()
            .values("type")
            .annotate(total=Sum("amount"))
        )

        result = {"income": 0.0, "expense": 0.0}
        for row in totals:
            result[row["type"]] = float(row["total"])

        return Response({
            "total_income": result["income"],
            "total_expenses": result["expense"],
            "net_balance": round(result["income"] - result["expense"], 2),
        })


class CategoryBreakdownView(APIView):
    permission_classes = [IsAnalystOrAbove]

    def get(self, request):
        rows = (
            active_records()
            .values("category", "type")
            .annotate(total=Sum("amount"), count=Count("id"))
            .order_by("-total")
        )

        return Response([
            {
                "category": r["category"],
                "type": r["type"],
                "total": float(r["total"]),
                "count": r["count"],
            }
            for r in rows
        ])


class MonthlyTrendsView(APIView):
    permission_classes = [IsAnalystOrAbove]

    def get(self, request):
        try:
            months = min(max(int(request.query_params.get("months", 6)), 1), 24)
        except (ValueError, TypeError):
            months = 6

        rows = (
            active_records()
            .annotate(month=TruncMonth("date"))
            .values("month", "type")
            .annotate(total=Sum("amount"))
            .order_by("month")
        )

        # Pivot into month -> {income, expense}
        trends = {}
        for row in rows:
            key = row["month"].strftime("%Y-%m")
            if key not in trends:
                trends[key] = {"month": key, "income": 0.0, "expense": 0.0}
            trends[key][row["type"]] = float(row["total"])

        sorted_trends = sorted(trends.values(), key=lambda x: x["month"])
        return Response(sorted_trends[-months:])


class RecentActivityView(APIView):
    permission_classes = [IsViewerOrAbove]

    def get(self, request):
        try:
            limit = min(int(request.query_params.get("limit", 10)), 50)
        except (ValueError, TypeError):
            limit = 10

        from api.serializers import FinancialRecordSerializer
        records = active_records()[:limit]
        return Response(FinancialRecordSerializer(records, many=True).data)
