from rest_framework.views import exception_handler as drf_exception_handler
from rest_framework.response import Response
from rest_framework import status


def exception_handler(exc, context):
    """
    Wraps DRF's default exception handler to give consistent error shapes.
    Every error response looks like: {"error": "..."} or {"errors": {...}}
    """
    response = drf_exception_handler(exc, context)

    if response is None:
        return Response(
            {"error": "An unexpected error occurred."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    data = response.data

    # DRF validation errors come back as a dict of field -> [messages]
    # We keep that shape but rename the key to "errors" for clarity
    if isinstance(data, dict):
        if "detail" in data:
            response.data = {"error": str(data["detail"])}
        elif any(isinstance(v, list) for v in data.values()):
            # flatten field errors into a simple list of strings
            flat = []
            for field, messages in data.items():
                if isinstance(messages, list):
                    for msg in messages:
                        flat.append(f"{field}: {msg}" if field != "non_field_errors" else str(msg))
                else:
                    flat.append(str(messages))
            response.data = {"errors": flat}

    return response


def paginate_queryset(queryset, request, default_per_page=20):
    """Simple manual pagination — returns (items, pagination_meta)."""
    try:
        page = max(int(request.query_params.get("page", 1)), 1)
        per_page = min(int(request.query_params.get("per_page", default_per_page)), 100)
    except (ValueError, TypeError):
        page, per_page = 1, default_per_page

    total = queryset.count()
    start = (page - 1) * per_page
    end = start + per_page

    return queryset[start:end], {
        "page": page,
        "per_page": per_page,
        "total": total,
        "pages": max((total + per_page - 1) // per_page, 1),
    }
