# Generated by Django 3.1.1 on 2020-10-01 13:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0012_user_is_reporting"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="has_completed_welcoming_tour",
            field=models.BooleanField(default=False, verbose_name="Parcours de bienvenue effectué"),
        ),
    ]
