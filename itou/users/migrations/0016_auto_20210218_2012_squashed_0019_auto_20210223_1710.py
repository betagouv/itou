# Generated by Django 3.1.5 on 2021-02-23 17:19

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    replaces = [
        ("users", "0016_auto_20210218_2012"),
        ("users", "0017_auto_20210218_2130"),
        ("users", "0018_auto_20210218_2133"),
        ("users", "0019_auto_20210223_1710"),
    ]

    dependencies = [
        ("asp", "__first__"),
        ("users", "0015_unique_emails_idx"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="birth_country",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="asp.country",
                verbose_name="Pays de naissance",
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="birth_place",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="asp.commune",
                verbose_name="Commune de naissance",
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="title",
            field=models.CharField(
                blank=True,
                choices=[("M", "Monsieur"), ("MME", "Madame")],
                max_length=3,
                null=True,
                verbose_name="Civilité",
            ),
        ),
        migrations.CreateModel(
            name="JobSeekerProfile",
            fields=[
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        primary_key=True,
                        related_name="jobseeker_profile",
                        serialize=False,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Demandeur d'emploi",
                    ),
                ),
                (
                    "education_level",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("00", "Personne avec qualifications non-certifiantes"),
                            ("01", "Jamais scolarisé"),
                            ("10", "Troisième cycle ou école d'ingénieur"),
                            ("20", "Formation de niveau licence"),
                            ("30", "Formation de niveau BTS ou DUT"),
                            ("40", "Formation de niveau BAC"),
                            ("41", "Brevet de technicien ou baccalauréat professionnel"),
                            ("50", "Formation de niveau BEP ou CAP"),
                            ("51", "Diplôme obtenu CAP ou BEP"),
                            ("60", "Formation courte d'une durée d'un an"),
                            ("70", "Pas de formation au-delà de la scolarité obligatoire"),
                        ],
                        max_length=2,
                        verbose_name="Niveau de formation (ASP)",
                    ),
                ),
                ("resourceless", models.BooleanField(default=False, verbose_name="Sans ressource")),
                ("rqth_employee", models.BooleanField(default=False, verbose_name="Employé RQTH")),
                ("oeth_employee", models.BooleanField(default=False, verbose_name="Employé OETH")),
                (
                    "poleemploi_since",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("LESS_THAN_6_MONTHS", "Moins de 6 mois"),
                            ("FROM_6_TO_11_MONTHS", "De 6 à 11 mois"),
                            ("FROM_12_TO_23_MONTHS", "De 12 à 23 mois"),
                            ("MORE_THAN_24_MONTHS", "24 mois et plus"),
                        ],
                        max_length=20,
                        verbose_name="Inscrit à Pôle emploi depuis",
                    ),
                ),
                (
                    "unemployed_since",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("LESS_THAN_6_MONTHS", "Moins de 6 mois"),
                            ("FROM_6_TO_11_MONTHS", "De 6 à 11 mois"),
                            ("FROM_12_TO_23_MONTHS", "De 12 à 23 mois"),
                            ("MORE_THAN_24_MONTHS", "24 mois et plus"),
                        ],
                        max_length=20,
                        verbose_name="Sans emploi depuis",
                    ),
                ),
                (
                    "rsa_allocation_since",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("LESS_THAN_6_MONTHS", "Moins de 6 mois"),
                            ("FROM_6_TO_11_MONTHS", "De 6 à 11 mois"),
                            ("FROM_12_TO_23_MONTHS", "De 12 à 23 mois"),
                            ("MORE_THAN_24_MONTHS", "24 mois et plus"),
                        ],
                        max_length=20,
                        verbose_name="Allocataire du RSA depuis",
                    ),
                ),
                (
                    "ass_allocation_since",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("LESS_THAN_6_MONTHS", "Moins de 6 mois"),
                            ("FROM_6_TO_11_MONTHS", "De 6 à 11 mois"),
                            ("FROM_12_TO_23_MONTHS", "De 12 à 23 mois"),
                            ("MORE_THAN_24_MONTHS", "24 mois et plus"),
                        ],
                        max_length=20,
                        verbose_name="Allocataire de l'ASS depuis",
                    ),
                ),
                (
                    "aah_allocation_since",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("LESS_THAN_6_MONTHS", "Moins de 6 mois"),
                            ("FROM_6_TO_11_MONTHS", "De 6 à 11 mois"),
                            ("FROM_12_TO_23_MONTHS", "De 12 à 23 mois"),
                            ("MORE_THAN_24_MONTHS", "24 mois et plus"),
                        ],
                        max_length=20,
                        verbose_name="Allocataire de l'AAH depuis",
                    ),
                ),
                (
                    "ata_allocation_since",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("LESS_THAN_6_MONTHS", "Moins de 6 mois"),
                            ("FROM_6_TO_11_MONTHS", "De 6 à 11 mois"),
                            ("FROM_12_TO_23_MONTHS", "De 12 à 23 mois"),
                            ("MORE_THAN_24_MONTHS", "24 mois et plus"),
                        ],
                        max_length=20,
                        verbose_name="Allocataire de l'ATA depuis",
                    ),
                ),
            ],
            options={
                "verbose_name": "Profil demandeur d'emploi",
                "verbose_name_plural": "Profils demandeur d'emploi",
            },
        ),
    ]