import json
from decimal import Decimal
from typing import Any

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from location.models import District, Division
from medihub import settings


class Command(BaseCommand):
  help = "Populate districts from dataset/district.json"

  def handle(self, *args: Any, **options: Any):
    file_path = settings.BASE_DIR / "dataset" / "district.json"

    if not file_path.exists():
      raise CommandError(f"District dataset not found: {file_path}")

    divisions = {
      division.division_id: division
      for division in Division.objects.all()
    }

    if not divisions:
      raise CommandError(
        "No divisions found. Run `python manage.py populated_division` first."
      )

    with open(file_path, "r", encoding="utf-8") as file:
      data = json.load(file)

    districts = []
    missing_division_ids = set()

    for item in data:
      division_id = int(item["division_id"])
      division = divisions.get(division_id)

      if division is None:
        missing_division_ids.add(division_id)
        continue

      districts.append(
        District(
          division=division,
          district_id=int(item["id"]),
          district_name_bn=item["bn_name"],
          district_name_eng=item["name"],
          lattitude=Decimal(item["lat"]),
          logitude=Decimal(item["lon"]),
        )
      )

    if missing_division_ids:
      missing_ids = ", ".join(str(item) for item in sorted(missing_division_ids))
      raise CommandError(
        f"District dataset refers to missing division_id values: {missing_ids}"
      )

    with transaction.atomic():
      deleted_count, _ = District.objects.all().delete()
      if deleted_count:
        self.stdout.write(
          self.style.WARNING(f"Removed {deleted_count} existing districts")
        )

      District.objects.bulk_create(districts)

    self.stdout.write(
      self.style.SUCCESS(f"Successfully populated {len(districts)} districts")
    )
