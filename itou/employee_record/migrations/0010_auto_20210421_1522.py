# Generated by Django 3.1.8 on 2021-04-21 13:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("employee_record", "0009_auto_20210416_1128"),
    ]

    operations = [
        migrations.AlterField(
            model_name="employeerecord",
            name="status",
            field=models.CharField(
                choices=[
                    ("NEW", "Nouvelle fiche salarié"),
                    ("READY", "Données complètes, prêtes à l'envoi ASP"),
                    ("SENT", "Envoyée ASP"),
                    ("REJECTED", "Rejet ASP"),
                    ("PROCESSED", "Traitée ASP"),
                    ("ARCHIVED", "Archivée"),
                ],
                default="NEW",
                max_length=10,
                verbose_name="Statut",
            ),
        ),
    ]
