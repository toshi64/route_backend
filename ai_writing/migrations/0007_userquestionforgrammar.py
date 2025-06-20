# Generated by Django 5.2 on 2025-06-11 01:28

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ai_writing', '0006_metaanalysisresult'),
        ('instant_feedback', '0007_finalanalysis'),
        ('material_scheduler', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserQuestionForGrammar',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('target', models.CharField(choices=[('ai', 'AI'), ('human', 'Human')], max_length=10)),
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
