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
        response_data = dict()

        for tettra_page_data in data:
            tettra_page_data["page_id"] = tettra_page_data.get("id", -1)
            page_id = tettra_page_data["page_id"]
            if any(
                [
                    tettra_page_data.get("category_id", None) is None,
                    tettra_page_data.get("category_name", None) is None,
                ]
            ):
                response_data[page_id] = "Skipping because of null category"
            elif tettra_page_data.get("deleted_at", None) is not None:
                TettraPage.objects.filter(page_id=page_id).delete()
                response_data[page_id] = "Deleted"
            else:
                try:
                    serializer = TettraPageSerializer(
                        TettraPage.objects.get(page_id=page_id), data=tettra_page_data, partial=True
                    )
                    response_data[page_id] = "Updated"
                except TettraPage.DoesNotExist:
                    serializer = TettraPageSerializer(data=tettra_page_data, partial=True)
                    response_data[page_id] = "Created"

                try:
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
                except BaseException as e:
                    response_data[page_id] = str(e)

        return response.Response(
            response_data,
            status=status.HTTP_200_OK,
        )
