def convert_django_validation_error_to_rest_framework_validation_error(exc, context):
    from django.core.exceptions import (
        NON_FIELD_ERRORS as DJANGO_NON_FIELD_ERRORS,
        ValidationError as DjangoValidationError,
    )

    from rest_framework.exceptions import ValidationError as DRFValidationError
    from rest_framework.views import api_settings, exception_handler as drf_exception_handler

    DRF_NON_FIELD_ERRORS = api_settings.NON_FIELD_ERRORS_KEY

    if isinstance(exc, DjangoValidationError):
        data = exc.message_dict
        if DJANGO_NON_FIELD_ERRORS in data:
            data[DRF_NON_FIELD_ERRORS] = data[DJANGO_NON_FIELD_ERRORS]
            del data[DJANGO_NON_FIELD_ERRORS]
        exc = DRFValidationError(detail=data)
    return drf_exception_handler(exc, context)
