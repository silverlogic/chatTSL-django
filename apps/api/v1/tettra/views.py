import json

from django.core.files.uploadedfile import InMemoryUploadedFile

from rest_framework import permissions, response, status, viewsets

from apps.tettra.models import TettraPage

from .serializers import TettraPageImportDumpSerializer, TettraPageSerializer


class TettraPageImportDumpViewSet(viewsets.GenericViewSet):
    serializer_class = TettraPageImportDumpSerializer
    permission_classes = [permissions.IsAdminUser]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        file: InMemoryUploadedFile = serializer.validated_data["file"]
        content: str = file.read()
        data = json.loads(content)
        pages_updated = 0
        pages_created = 0

        for tettra_page_data in data:
            tettra_page_data["page_id"] = tettra_page_data.get("id", -1)
            try:
                page_id = tettra_page_data["page_id"]
                serializer = TettraPageSerializer(
                    TettraPage.objects.get(page_id=page_id), data=tettra_page_data, partial=True
                )
                pages_updated += 1
            except TettraPage.DoesNotExist:
                serializer = TettraPageSerializer(data=tettra_page_data, partial=True)
                pages_created += 1

            serializer.is_valid(raise_exception=True)
            serializer.save()

        return response.Response(
            dict(pages_created=pages_created, pages_updated=pages_updated),
            status=status.HTTP_201_CREATED,
        )
