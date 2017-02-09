from django.utils.translation import ugettext_lazy as _

from drf_extra_fields.fields import Base64ImageField
from easy_thumbnails.files import get_thumbnailer
from phonenumber_field.phonenumber import to_python
from rest_framework import serializers


class ThumbnailImageField(Base64ImageField):
    def __init__(self, *args, **kwargs):
        self.sizes = kwargs.pop('sizes', {})
        super(ThumbnailImageField, self).__init__(*args, **kwargs)

    def to_representation(self, value):
        if not value:
            return None

        if not getattr(value, 'url', None):
            # If the file has not been saved it may not have a URL.
            return None
        url = value.url
        request = self.context.get('request', None)
        if request is not None:
            url = request.build_absolute_uri(url)

        sizes = {
            'full_size': url
        }

        thumbnailer = get_thumbnailer(value)
        for name, size in self.sizes.items():
            url = thumbnailer.get_thumbnail({'size': size}).url
            if request is not None:
                url = request.build_absolute_uri(url)
            sizes[name] = url

        return sizes


class PhoneNumberField(serializers.CharField):
    default_error_messages = {
        'invalid': _('Enter a valid phone number.'),
    }

    def to_internal_value(self, data):
        phone_number = to_python(data)
        if phone_number and not phone_number.is_valid():
            raise serializers.ValidationError(self.error_messages['invalid'])
        return phone_number
