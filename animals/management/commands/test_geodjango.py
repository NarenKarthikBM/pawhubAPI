from django.contrib.gis.geos import Point
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Test GeoDjango installation and database connectivity"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Testing GeoDjango installation..."))

        try:
            # Test GEOS functionality
            point = Point(-122.4194, 37.7749)  # San Francisco coordinates
            self.stdout.write(
                self.style.SUCCESS(f"✓ GEOS working: Created point at {point}")
            )

            # Test database connection with spatial queries
            from django.db import connection

            with connection.cursor() as cursor:
                cursor.execute("SELECT PostGIS_Version();")
                version = cursor.fetchone()[0]
                self.stdout.write(self.style.SUCCESS(f"✓ PostGIS version: {version}"))

            # Test spatial query capability
            from animals.models import AnimalProfileModel

            count = AnimalProfileModel.objects.filter(location__isnull=False).count()
            self.stdout.write(
                self.style.SUCCESS(
                    f"✓ Found {count} animal profiles with location data"
                )
            )

            self.stdout.write(
                self.style.SUCCESS("GeoDjango setup appears to be working correctly!")
            )

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ GeoDjango test failed: {e}"))
            return
