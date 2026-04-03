from datetime import datetime, timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from api.models import FinancialRecord
from api.serializers import FinancialRecordSerializer, RecordWriteSerializer
from api.permissions import IsViewerOrAbove, IsAnalystOrAbove, IsAdmin
from api.utils import paginate_queryset


def apply_filters(queryset, params):
    """Keeps the view handler itself clean by isolating filter logic here."""
    if params.get("type"):
        queryset = queryset.filter(type=params["type"])

    if params.get("category"):
        queryset = queryset.filter(category__icontains=params["category"])

    if params.get("from_date"):
        try:
            from_date = datetime.strptime(params["from_date"], "%Y-%m-%d").date()
            queryset = queryset.filter(date__gte=from_date)
        except ValueError:
            pass

    if params.get("to_date"):
        try:
            to_date = datetime.strptime(params["to_date"], "%Y-%m-%d").date()
            queryset = queryset.filter(date__lte=to_date)
        except ValueError:
            pass

    return queryset


class RecordListView(APIView):
    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAnalystOrAbove()]
        return [IsViewerOrAbove()]

    def get(self, request):
        queryset = FinancialRecord.objects.filter(deleted_at__isnull=True)
        queryset = apply_filters(queryset, request.query_params)

        records, pagination = paginate_queryset(queryset, request)
        return Response({
            "records": FinancialRecordSerializer(records, many=True).data,
            "pagination": pagination,
        })

    def post(self, request):
        serializer = RecordWriteSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"errors": serializer.errors}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        record = serializer.save(created_by=request.user)
        return Response(FinancialRecordSerializer(record).data, status=status.HTTP_201_CREATED)


class RecordDetailView(APIView):
    def get_permissions(self):
        if self.request.method in ("PUT", "DELETE"):
            return [IsAdmin()]
        return [IsViewerOrAbove()]

    def _get_record(self, record_id):
        try:
            return FinancialRecord.objects.get(pk=record_id, deleted_at__isnull=True)
        except FinancialRecord.DoesNotExist:
            return None

    def get(self, request, record_id):
        record = self._get_record(record_id)
        if not record:
            return Response({"error": "Record not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(FinancialRecordSerializer(record).data)

    def put(self, request, record_id):
        record = self._get_record(record_id)
        if not record:
            return Response({"error": "Record not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = RecordWriteSerializer(instance=record, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response({"errors": serializer.errors}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        record = serializer.save()
        return Response(FinancialRecordSerializer(record).data)

    def delete(self, request, record_id):
        record = self._get_record(record_id)
        if not record:
            return Response({"error": "Record not found"}, status=status.HTTP_404_NOT_FOUND)

        record.deleted_at = datetime.now(timezone.utc)
        record.save()
        return Response({"message": "Record deleted"})
