# myapp/renderers.py
from rest_framework.renderers import JSONRenderer


class StandardizedJSONRenderer(JSONRenderer):
    """
    Custom renderer to guarantee a uniform structure for all API outputs.
    """

    def render(self, data, accepted_media_type=None, renderer_context=None):
        response = renderer_context.get('response')
        status_code = response.status_code

        # Check if the payload is already an error structure from DRF exception handlers
        is_success = 200 <= status_code < 300

        # Build your standardized shell
        standardized_response = {
            "success": is_success,
            "status_code": status_code,
            "message": "Operation successful" if is_success else "An error occurred",
            "data": None,
            "errors": None
        }

        if is_success:
            standardized_response["data"] = data
        else:
            # Handle default DRF validation and exception dictionaries
            standardized_response["errors"] = data
            if isinstance(data, dict) and "detail" in data:
                standardized_response["message"] = data["detail"]

        return super().render(standardized_response, accepted_media_type, renderer_context)
