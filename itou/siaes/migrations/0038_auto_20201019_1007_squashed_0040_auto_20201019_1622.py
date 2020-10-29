# Generated by Django 3.1 on 2020-10-29 10:09

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    replaces = [('siaes', '0038_auto_20201019_1007'), ('siaes', '0039_auto_20201019_1019'), ('siaes', '0040_auto_20201019_1622')]

    dependencies = [
        ('siaes', '0037_auto_20201009_1619'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='siaemembership',
            name='is_active',
            field=models.BooleanField(default=True, verbose_name='Rattachement actif'),
        ),
        migrations.AddField(
            model_name='siaemembership',
            name='updated_at',
            field=models.DateTimeField(null=True, verbose_name='Date de mise à jour'),
        ),
        migrations.AddField(
            model_name='siaemembership',
            name='updated_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='siae_membership_updated_by', to=settings.AUTH_USER_MODEL, verbose_name='Mis à jour par'),
        ),
    ]
