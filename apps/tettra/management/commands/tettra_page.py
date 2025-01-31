import json
from pathlib import Path

from django.core.management.base import BaseCommand

from apps.api.v1.tettra.serializers import TettraPageSerializer
from apps.tettra.models import TettraPage


class Command(BaseCommand):
    help = f"{TettraPage._meta.verbose_name.title()} Management"

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    def add_arguments(self, parser):
        parser.add_argument(
            "--import_json", type=str, help=f"Import {TettraPage._meta.verbose_name_plural.title()}"
        )
        parser.add_argument("--regenerate_embeddings", action="store_true", default=False)
        parser.add_argument(
            "--tettra_page",
            type=int,
            nargs=1,
        )

    def handle(self, *args, **options):
        try:
            self._handle(*args, **options)
        except BaseException as e:
            self.stdout.write("\r\n")
            if isinstance(e, KeyboardInterrupt):
                return
            raise e

    def _handle(self, *args, **options):
        regenerate_embeddings: bool = options.get("regenerate_embeddings")

        if file_path := options.get("import_json"):
            self.import_json(Path(file_path))
        if regenerate_embeddings:
            if tettra_page_id := options.get("tettra_page"):
                self.regenerate_embeddings(tettra_page_id=tettra_page_id[0])
            else:
                self.regenerate_embeddings(tettra_page_id=None)

    def import_json(self, file_path: Path):
        content = file_path.read_text()
        data = json.loads(content)

        for tettra_page_data in data:
            tettra_page_data["page_id"] = tettra_page_data["id"]
            page_id = tettra_page_data["page_id"]
            self.stdout.write(
                self.style.MIGRATE_HEADING(
                    f"Importing {TettraPage._meta.verbose_name.title()}(page_id:{page_id})"
                )
            )

            if any(
                [
                    tettra_page_data.get("category_id", None) is None,
                    tettra_page_data.get("category_name", None) is None,
                ]
            ):
                self.stdout.write(
                    self.style.ERROR_OUTPUT("Skipping because page has null category")
                )
            elif tettra_page_data.get("deleted_at", None) is not None:
                TettraPage.objects.filter(page_id=page_id).delete()
                self.stdout.write(self.style.ERROR_OUTPUT("Skipping because page is deleted"))
            else:
                category_data = dict(
                    category_id=tettra_page_data.pop("category_id"),
                    category_name=tettra_page_data.pop("category_name"),
                )
                subcategory_data: dict = None
                if all(
                    [
                        tettra_page_data.get("subcategory_id", None) is not None,
                        tettra_page_data.get("subcategory_name", None) is not None,
                    ]
                ):
                    subcategory_data = dict(
                        subcategory_id=tettra_page_data.pop("subcategory_id"),
                        subcategory_name=tettra_page_data.pop("subcategory_name"),
                    )

                serializer: TettraPageSerializer
                try:
                    serializer = TettraPageSerializer(
                        TettraPage.objects.get(page_id=page_id), data=tettra_page_data, partial=True
                    )
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Updating existing {TettraPage._meta.verbose_name.title()}"
                        )
                    )
                except TettraPage.DoesNotExist:
                    serializer = TettraPageSerializer(data=tettra_page_data, partial=True)
                    self.stdout.write(
                        self.style.SUCCESS(f"Creating new {TettraPage._meta.verbose_name.title()}")
                    )

                try:
                    serializer.is_valid(raise_exception=True)
                    serializer.save(category=category_data, subcategory=subcategory_data)
                except BaseException as e:
                    self.stdout.write(self.style.ERROR(str(e)))

    def regenerate_embeddings(self, tettra_page_id: int | None):
        from ...tasks import generate_vector_embeddings
        
        queryset = TettraPage.objects.all()
        if isinstance(tettra_page_id, int):
            queryset = queryset.filter(id=tettra_page_id)
        for tettra_page in queryset:
            tettra_page.chunks.all().delete()
            generate_vector_embeddings(tettra_page=tettra_page.id)
