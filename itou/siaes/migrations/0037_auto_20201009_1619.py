# Generated by Django 3.1.2 on 2020-10-09 14:19

from django.db import migrations, models

import itou.utils.validators


class Migration(migrations.Migration):

    dependencies = [
        ("siaes", "0036_auto_20201006_1755"),
    ]

    operations = [
        migrations.RemoveField(model_name="siae", name="convention_end_date",),
        migrations.RemoveField(model_name="siae", name="deactivated_at",),
        migrations.RemoveField(model_name="siae", name="external_id",),
        migrations.RemoveField(model_name="siae", name="is_active",),
        migrations.RemoveField(model_name="siae", name="reactivated_at",),
        migrations.RemoveField(model_name="siae", name="reactivated_by",),
        migrations.AlterField(
            model_name="siaeconvention",
            name="siret_signature",
            field=models.CharField(
                db_index=True,
                max_length=14,
                validators=[itou.utils.validators.validate_siret],
                verbose_name="Siret à la signature",
            ),
        ),
        migrations.AlterField(
            model_name="siaefinancialannex",
            name="state",
            field=models.CharField(
                choices=[
                    ("VALIDE", "Validée"),
                    ("PROVISOIRE", "Provisoire (valide)"),
                    ("HISTORISE", "Archivée (invalide)"),
                    ("ANNULE", "Annulée"),
                    ("SAISI", "Saisie (invalide)"),
                    ("BROUILLON", "Brouillon (invalide)"),
                    ("CLOTURE", "Cloturée (invalide)"),
                    ("REJETE", "Rejetée"),
                ],
                max_length=20,
                verbose_name="Etat",
            ),
        ),
    ]