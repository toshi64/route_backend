# Generated by Django 5.2 on 2025-06-11 08:00

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ai_writing', '0007_userquestionforgrammar'),
        ('instant_feedback', '0007_finalanalysis'),
        ('material_scheduler', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='QuestionClipForGrammar',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('content', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('answer_unit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ai_writing.answerunit')),
                ('grammar_question', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='ai_writing.grammarquestion')),
                ('schedule_component', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='material_scheduler.schedulecomponent')),
                ('session', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='instant_feedback.session')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
