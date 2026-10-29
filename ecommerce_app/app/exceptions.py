# myapp/exceptions.py
from rest_framework.views import exception_handler
from rest_framework.exceptions import ValidationError


def custom_exception_handler(exc, context):
    # Call DRF's default handler first to get the standard error response
    response = exception_handler(exc, context)

    if response is not None:
        # Standardize the structure for validation errors explicitly
        if isinstance(exc, ValidationError):
            response.data = {
                "detail": "Validation failed.",
                "fields": response.data  # Preserves field-specific validation errors
            }
        else:
            response.data = {
                "detail": response.data.get("detail", str(exc))
            }

    return response
