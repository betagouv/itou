# Generated by Django 3.1.5 on 2021-02-02 13:49

import django.contrib.postgres.constraints
import django.contrib.postgres.fields.ranges
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models

import itou.utils.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("siaes", "0043_siaemembership_notifications"),
        ("approvals", "0011_suspension_create_trigger"),
    ]

    operations = [
        migrations.CreateModel(
            name="Prolongation",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "start_at",
                    models.DateField(db_index=True, default=django.utils.timezone.now, verbose_name="Date de début"),
                ),
                (
                    "end_at",
                    models.DateField(db_index=True, default=django.utils.timezone.now, verbose_name="Date de fin"),
                ),
                (
                    "reason",
                    models.CharField(
                        choices=[
                            ("COMPLETE_TRAINING", "Achever une formation (6 mois maximum)"),
                            ("RQTH", "RQTH (reconnaissance de la qualité de travailleur handicapé)"),
                            ("SENIOR", "Senior (+50 ans)"),
                            (
                                "PARTICULAR_DIFFICULTIES",
                                "Difficultés particulières qui font obstacle à l'insertion durable dans l’emploi",
                            ),
                        ],
                        default="COMPLETE_TRAINING",
                        max_length=30,
                        verbose_name="Motif",
                    ),
                ),
                ("reason_explanation", models.TextField(blank=True, verbose_name="Motivez la demande")),
                (
                    "is_valid",
                    models.BooleanField(
                        default=False, help_text="Précise si la prolongation est validée.", verbose_name="Validée"
                    ),
                ),
                ("validated_at", models.DateTimeField(null=True, verbose_name="Date de la validation")),
                (
                    "created_at",
                    models.DateTimeField(default=django.utils.timezone.now, verbose_name="Date de création"),
                ),
                ("updated_at", models.DateTimeField(blank=True, null=True, verbose_name="Date de modification")),
                (
                    "approval",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="approvals.approval", verbose_name="PASS IAE"
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="approvals_prolongated_set",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Créé par",
                    ),
                ),
                (
                    "siae",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="approvals_prolongated",
                        to="siaes.siae",
                        verbose_name="SIAE",
                    ),
                ),
                (
                    "updated_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Mis à jour par",
                    ),
                ),
                (
                    "validated_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="approvals_prolongations_validated",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Validé par",
                    ),
                ),
            ],
            options={
                "verbose_name": "Prolongation",
                "verbose_name_plural": "Prolongations",
                "ordering": ["-start_at"],
            },
        ),
        migrations.AddConstraint(
            model_name="prolongation",
            constraint=django.contrib.postgres.constraints.ExclusionConstraint(
                expressions=(
                    (
                        itou.utils.models.DateRange(
                            "start_at",
                            "end_at",
                            django.contrib.postgres.fields.ranges.RangeBoundary(
                                inclusive_lower=True, inclusive_upper=True
                            ),
                        ),
                        "&&",
                    ),
                    ("approval", "="),
                ),
                name="exclude_overlapping_prolongations",
            ),
        ),
    ]
