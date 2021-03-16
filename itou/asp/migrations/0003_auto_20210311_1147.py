# Generated by Django 3.1.7 on 2021-03-11 10:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("asp", "0002_auto_20210218_2051"),
    ]

    operations = [
        migrations.AlterField(
            model_name="country",
            name="group",
            field=models.CharField(
                choices=[("1", "France"), ("2", "CEE"), ("3", "Hors CEE")], max_length=15, verbose_name="Groupe"
            ),
        ),
    ]