from drf_extra_fields.fields import Base64ImageField
from easy_thumbnails.files import get_thumbnailer


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
