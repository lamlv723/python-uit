import os
from django.core.management.base import BaseCommand
from django.db import connection, transaction

class Command(BaseCommand):
    help = 'Loads initial data from load_data_modified.sql into the database.'

    def handle(self, *args, **options):
        sql_file_path = 'load_data_modified.sql' # Đảm bảo file này nằm ở thư mục gốc của dự án

        if not os.path.exists(sql_file_path):
            self.stdout.write(self.style.ERROR(f"Error: SQL file not found at {sql_file_path}"))
            return

        self.stdout.write(self.style.SUCCESS(f"Attempting to load data from {sql_file_path}..."))

        try:
            with open(sql_file_path, 'r', encoding='utf-8') as f:
                sql_statements = f.read()

            # Split SQL statements by semicolon, but be careful with semicolons inside strings.
            # A more robust solution might require a proper SQL parser.
            # For simple INSERT statements like yours, splitting by ';\n' is usually sufficient.
            statements = [s.strip() for s in sql_statements.split(';') if s.strip()]

            with transaction.atomic():
                with connection.cursor() as cursor:
                    for statement in statements:
                        try:
                            cursor.execute(statement)
                            # self.stdout.write(self.style.MIGRATE_HEADING(f"Executed: {statement[:50]}...")) # Optional: print executed SQL
                        except Exception as e:
                            self.stdout.write(self.style.ERROR(f"Error executing statement: {statement[:100]}... \nError: {e}"))
                            raise # Re-raise the exception to trigger rollback

            self.stdout.write(self.style.SUCCESS('Successfully loaded data from SQL file.'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'An error occurred during SQL loading: {e}'))
            # Rollback is automatic with transaction.atomic() on exception