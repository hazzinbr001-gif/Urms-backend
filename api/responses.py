from rest_framework.response import Response

def standard_response(status="success", message="", data=None, errors=None, meta=None, http_status=200):
    """
    Standardized API response format as required by the enterprise architecture.
    """
    response_data = {
        "status": status,
        "message": message,
        "data": data if data is not None else {},
        "errors": errors if errors is not None else [],
        "meta": meta if meta is not None else {}
    }
    return Response(response_data, status=http_status)

def success_response(message="", data=None, meta=None, http_status=200):
    return standard_response(status="success", message=message, data=data, meta=meta, http_status=http_status)

def error_response(message="An error occurred", errors=None, http_status=400):
    return standard_response(status="error", message=message, errors=errors, http_status=http_status)
