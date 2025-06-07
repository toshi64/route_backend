from django.core.management.base import BaseCommand
from ai_writing.models import GrammarNote
import csv
import uuid
import os
from django.utils.timezone import now

class Command(BaseCommand):
    help = 'Import grammar notes from CSV'

    def handle(self, *args, **options):
        file_path = os.path.join(os.path.dirname(__file__), 'grammar_note.csv')
        if not os.path.exists(file_path):
            self.stderr.write(self.style.ERROR(f'File not found: {file_path}'))
            return

        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            count = 0
            for row in reader:
                GrammarNote.objects.create(
                    custom_id=row.get('custom_id') or str(uuid.uuid4()),
                    created_by=row.get('created_by') or "unknown",
                    version=row.get('version') or '1.0',
                    subgenre=row.get('subgenre', '').strip(),
                    title=row.get('title', '').strip(),
                    description=row.get('description（マークダウン）', '').strip(),
                    created_at=now(),
                    updated_at=now()
                )
                count += 1

        self.stdout.write(self.style.SUCCESS(f'Successfully imported {count} grammar notes.'))
