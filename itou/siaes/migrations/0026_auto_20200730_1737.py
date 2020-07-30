# Generated by Django 3.0.7 on 2020-07-30 15:37

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("siaes", "0025_auto_20200723_1447")]

    operations = [
        migrations.AddField(
            model_name="siae",
            name="parent",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="children",
                to="siaes.Siae",
                verbose_name="Structure mère",
            ),
        ),
        migrations.AlterField(
            model_name="siae",
            name="active_until",
            field=models.DateTimeField(blank=True, null=True, verbose_name="Date de désactivation"),
        ),
    ]
