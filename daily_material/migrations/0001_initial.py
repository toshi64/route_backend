# Generated by Django 5.2 on 2025-05-26 06:17

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('instant_feedback', '0007_finalanalysis'),
    ]

    operations = [
        migrations.CreateModel(
            name='CurriculumPlan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('summary_text', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('final_analysis', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='curriculum_plan', to='instant_feedback.finalanalysis')),
            ],
        ),
        migrations.CreateModel(
            name='CurriculumDay',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day', models.PositiveSmallIntegerField()),
                ('title', models.CharField(max_length=100)),
                ('objective', models.TextField()),
                ('focus', models.TextField()),
                ('tag', models.CharField(max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('curriculum_plan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='days', to='daily_material.curriculumplan')),
            ],
            options={
                'ordering': ['curriculum_plan', 'day'],
                'unique_together': {('curriculum_plan', 'day')},
            },
        ),
    ]
