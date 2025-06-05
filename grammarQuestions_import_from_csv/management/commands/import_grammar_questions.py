# grammar/management/commands/import_grammar_questions.py

from django.core.management.base import BaseCommand
from ai_writing.models import GrammarQuestion
import csv
import os
from django.utils.timezone import now

class Command(BaseCommand):
    help = 'Import grammar questions from grammar_questions.csv'

    def handle(self, *args, **options):
        file_path = os.path.join(os.path.dirname(__file__), 'grammar_questions.csv')
        if not os.path.exists(file_path):
            self.stderr.write(self.style.ERROR(f'File not found: {file_path}'))
            return

        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                GrammarQuestion.objects.create(
                    custom_id=row.get('custom_id') or None,
                    created_by=row['created_by'],
                    version=float(row['version']) if row['version'] else 1.0,
                    question_text=row['question_text'],
                    genre=row['genre'],
                    subgenre=row['subgenre'],
                    level=int(row['level']) if row['level'] else 1,
                    type=row['type'],
                    difficulty=int(row['difficulty']) if row['difficulty'] else 1,
                    importance=int(row['importance']) if row['importance'] else 1,
                    answer=row['answer'],
                    source=row['source'],
                    is_active=(row['is_active'].strip().upper() == 'TRUE'),
                    created_at=now(),
                    updated_at=now(),
                )

        self.stdout.write(self.style.SUCCESS('Grammar questions imported successfully'))
