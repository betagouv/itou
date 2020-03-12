# Generated by Django 2.2.10 on 2020-02-27 16:55
import csv
import os

from django.conf import settings
from django.db import migrations

from itou.siaes.models import Siae


KINDS = dict(Siae.KIND_CHOICES).keys()

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))

ASP_CSV_FILE = f"{settings.APPS_DIR}/siaes/management/commands/data/2020_02_siae_auth_email_and_external_id.csv"


def get_siret_kind_to_data_map():
    siret_kind_to_data_map = {}

    with open(ASP_CSV_FILE) as csvfile:
        reader = csv.reader(csvfile, delimiter=";")
        for i, row in enumerate(reader):
            assert len(row) == 5
            if i == 0:  # Skip CSV header.
                continue
            external_id = int(row[0])
            assert external_id > 0
            siret = row[1]
            assert len(siret) == 14
            kind = row[3]
            if kind not in KINDS:
                continue
            auth_email = row[4].strip()
            if "@" not in auth_email:
                continue
            assert " " not in auth_email
            key = (siret, kind)
            if key in siret_kind_to_data_map:
                assert siret_kind_to_data_map[key]["auth_email"] == auth_email
            else:
                siret_kind_to_data_map[key] = {"auth_email": auth_email, "external_id": external_id}

    return siret_kind_to_data_map


SIRET_KIND_TO_DATA_MAP = get_siret_kind_to_data_map()


def populate_siae_external_id_and_update_auth_email(apps, schema_editor):
    print()  # New line so that logs below are more readable.
    auth_email_update_counter = 0
    for siae in Siae.objects.all():
        key = (siae.siret, siae.kind)
        if key not in SIRET_KIND_TO_DATA_MAP:
            continue
        auth_email = SIRET_KIND_TO_DATA_MAP[key]["auth_email"]
        external_id = SIRET_KIND_TO_DATA_MAP[key]["external_id"]
        if siae.auth_email != auth_email:
            print(f"auth_email {siae.auth_email} changed to {auth_email} (siret={siae.siret} kind={siae.kind})")
            siae.auth_email = auth_email
            auth_email_update_counter += 1
        siae.external_id = external_id
        siae.save()

    for siae in Siae.objects.all():
        if not siae.has_members and not siae.auth_email:
            msg = (
                f"Signup is impossible for siae siret={siae.siret} "
                f"kind={siae.kind} dpt={siae.department} source={siae.source} "
                f"created_by={siae.created_by} siae_email={siae.email}"
            )
            print(msg)

    print(f"A total of {auth_email_update_counter} auth_emails were updated.")


class Migration(migrations.Migration):

    dependencies = [("siaes", "0019_auto_20200210_1626")]

    operations = [migrations.RunPython(populate_siae_external_id_and_update_auth_email, migrations.RunPython.noop)]
