# Generated by Django 3.1.8 on 2021-04-30 15:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("job_applications", "0029_auto_20210223_1528"),
    ]

    operations = [
        migrations.AddField(
            model_name="jobapplication",
            name="resume_link",
            field=models.URLField(blank=True, max_length=500, verbose_name="Lien vers un CV"),
        ),
    ]