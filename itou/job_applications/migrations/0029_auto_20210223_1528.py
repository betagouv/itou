# Generated by Django 3.1.7 on 2021-02-23 14:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("job_applications", "0028_auto_20201002_1408"),
    ]

    operations = [
        migrations.AlterField(
            model_name="jobapplication",
            name="hiring_end_at",
            field=models.DateField(blank=True, null=True, verbose_name="Date prévisionnelle de fin du contrat"),
        ),
    ]