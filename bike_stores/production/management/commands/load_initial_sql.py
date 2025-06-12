import os
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import connection, transaction

class Command(BaseCommand):
    help = 'Loads initial data from load_data_modified.sql into the database.'

    def handle(self, *args, **options):
        sql_file_path = os.path.join(settings.BASE_DIR, 'load_data_modified.sql')

        if not os.path.exists(sql_file_path):
            self.stdout.write(self.style.ERROR(f"Error: SQL file not found at {sql_file_path}"))
            return

        self.stdout.write(self.style.SUCCESS(f"Attempting to load data from {sql_file_path}..."))

        try:
            with open(sql_file_path, 'r', encoding='utf-8') as f:
                sql_script = f.read()

                with transaction.atomic():
                    with connection.cursor() as cursor:
                        cursor.execute(sql_script)

            self.stdout.write(self.style.SUCCESS('Successfully loaded data from SQL file.'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'An error occurred during SQL loading: {e}'))