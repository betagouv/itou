"""
This script exports ASP reference files into fixtures

This could be a "one shot" but we don't know for sure if this
reference files are likely to change
"""
import json
import logging
import os
from datetime import datetime

import pandas as pd
from django.core.management.base import BaseCommand


_IMPORT_DIR = "imports"
_FIXTURES_DIR = "itou/asp/fixtures"
_SEP = ";"
_ASP_DATE_FORMAT = "%d/%m/%Y"


def parse_asp_date(dt):
    # Sometimes import files have a / instead of empty string for end dates
    if dt and dt != "/":
        return str(datetime.strptime(dt, _ASP_DATE_FORMAT).date())
    else:
        return None


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("--dry-run", dest="dry_run", action="store_true", help="Only print data to import")

    def set_logger(self, verbosity):
        """
        Set logger level based on the verbosity option.
        """
        handler = logging.StreamHandler(self.stdout)

        self.logger = logging.getLogger(__name__)
        self.logger.propagate = False
        self.logger.addHandler(handler)

        self.logger.setLevel(logging.INFO)
        if verbosity > 1:
            self.logger.setLevel(logging.DEBUG)

    def log(self, message):
        self.logger.debug(message)

    def load_dataframe(self, path, separator=_SEP):
        self.log(f"Creating dataframe from file: {path}")
        df = pd.read_csv(path, sep=separator)
        df = df.where(pd.notnull(df), None)
        self.log(df)
        return df

    def write_fixture_file(self, path, records):
        self.log(f"Formatted {len(records)} element(s)")
        self.log(f"Writing JSON fixture to: {path}")

        if not self.dry_run:
            with open(path, "w") as of:
                of.write(json.dumps(records))
        else:
            self.log("joking: DRY-RUN enabled")
        self.log("Done!")
        self.log("-" * 80)

    def file_exists(self, path):
        if os.path.isfile(path):
            self.log(f"Found input file '{path}'")
            return True
        self.log("No import file found. Skipping.")
        self.log("-" * 80)
        return False

    def gen_education_levels(self, filename="ref_niveau_formation.csv"):
        """
        Generate ASP education level fixture
        """
        path = os.path.join(_IMPORT_DIR, filename)

        self.log("Importing ASP education levels:\n")

        if not self.file_exists(path):
            return

        export_path = os.path.join(_FIXTURES_DIR, "asp_education_levels.json")
        model = "asp.EducationLevel"
        df = self.load_dataframe(path)
        records = []

        for idx, row in df.iterrows():
            start_date = parse_asp_date(row["rte_date_debut_effet"])
            end_date = parse_asp_date(row["rte_date_fin_effet"])

            elt = {
                "model": model,
                "pk": row["rnf_id"],
                "fields": {
                    "code": row["rnf_code_form_empl"],
                    "name": row["rnf_libelle_niveau_form_empl"],
                    "start_date": start_date,
                    "end_date": end_date,
                },
            }
            records.append(elt)

        self.write_fixture_file(export_path, records)

    def gen_insee_communes(self, filename="ref_insee_com.csv"):
        """
        Generates ASP INSEE communes fixture.

        Important:
        This list of communes is not the same as the official INSEE one.
        There is a reconciliation mechanism to implement
        """
        path = os.path.join(_IMPORT_DIR, filename)

        self.log("Importing ASP INSEE communes:\n")

        if not self.file_exists(path):
            return

        export_path = os.path.join(_FIXTURES_DIR, "asp_INSEE_communes.json")
        model = "asp.Commune"
        df = self.load_dataframe(path)
        records = []

        for idx, row in df.iterrows():
            start_date = parse_asp_date(row["DATE_DEB_INSEE"])
            end_date = parse_asp_date(row["DATE_FIN_INSEE"])

            elt = {
                "model": model,
                "pk": idx + 1,
                "fields": {
                    "code": row["CODE_COM_INSEE"],
                    "name": row["LIB_COM"],
                    "start_date": start_date,
                    "end_date": end_date,
                },
            }
            records.append(elt)

        self.write_fixture_file(export_path, records)

    def gen_insee_departments(self, filename="ref_insee_dpt.csv"):
        """
        Generates ASP INSEE department fixture.

        Important:
        This list of departments is not the same as the official INSEE one.
        There is a reconciliation mechanism to implement
        """
        path = os.path.join(_IMPORT_DIR, filename)

        self.log("Importing ASP INSEE departments:\n")

        if not self.file_exists(path):
            return

        export_path = os.path.join(_FIXTURES_DIR, "asp_INSEE_departments.json")
        model = "asp.Department"
        df = self.load_dataframe(path)
        records = []

        for idx, row in df.iterrows():
            start_date = parse_asp_date(row["DATE_DEB_DPT"])
            end_date = parse_asp_date(row["DATE_FIN_DPT"])

            elt = {
                "model": model,
                "pk": idx + 1,
                "fields": {
                    "code": row["CODE_DPT"],
                    "name": row["LIB_DPT"],
                    "start_date": start_date,
                    "end_date": end_date,
                },
            }
            records.append(elt)

        self.write_fixture_file(export_path, records)

    def gen_insee_countries(self, filename="ref_insee_pays.csv"):
        """
        Generates ASP INSEE countries fixture.

        This list of countries is not the same as the official INSEE one.
        In this specific case, we don't care. Itou is France-centric
        """
        path = os.path.join(_IMPORT_DIR, filename)

        self.log("Importing ASP INSEE countries:\n")

        if not self.file_exists(path):
            return

        export_path = os.path.join(_FIXTURES_DIR, "asp_INSEE_countries.json")
        model = "asp.Country"
        df = self.load_dataframe(path)
        records = []

        for idx, row in df.iterrows():
            elt = {
                "model": model,
                "pk": idx + 1,
                "fields": {
                    "code": row["CODE_INSEE_PAYS"],
                    "name": row["LIB_INSEE_PAYS"],
                    "group": row["CODE_GROUPE_PAYS"],
                    # For compatibility, no usage right now
                    "department": row["CODE_DPT"],
                },
            }
            records.append(elt)

        self.write_fixture_file(export_path, records)

    def gen_measures(self, filename="ref_mesure.csv"):
        """
        Generates ASP INSEE mesures fixture.
        """
        path = os.path.join(_IMPORT_DIR, filename)

        self.log("Importing ASP measures:\n")

        if not self.file_exists(path):
            return

        export_path = os.path.join(_FIXTURES_DIR, "asp_measures.json")
        model = "asp.Measure"
        df = self.load_dataframe(path)
        records = []

        for idx, row in df.iterrows():
            start_date = parse_asp_date(row["Rme_date_debut_effet"])
            end_date = parse_asp_date(row["Rme_date_fin_effet"])
            elt = {
                "model": model,
                "pk": row["Rme_id"],
                "fields": {
                    "code": row["Rme_code_mesure_disp"],
                    "display_code": row["Rme_code_mesure"],
                    "help_code": row["Rme_code_aide"],
                    "name": row["Rme_libelle_mesure"],
                    # For compatibility, no usage right now
                    "rdi_id": row["Rdi_id"],
                    "start_date": start_date,
                    "end_date": end_date,
                },
            }
            records.append(elt)

        self.write_fixture_file(export_path, records)

    def gen_employer_types(self, filename="ref_type_employeur.csv"):
        """
        Generates ASP employer types fixture.
        """
        path = os.path.join(_IMPORT_DIR, filename)

        self.log("Importing ASP employer types:\n")

        if not self.file_exists(path):
            return

        export_path = os.path.join(_FIXTURES_DIR, "asp_employer_types.json")
        model = "asp.EmployerType"
        df = self.load_dataframe(path)
        records = []

        for idx, row in df.iterrows():
            start_date = parse_asp_date(row["rte_date_debut_effet"])
            end_date = parse_asp_date(row["rte_date_fin_effet"])
            elt = {
                "model": model,
                "pk": row["rte_id"],
                "fields": {
                    "code": row["rte_code_type_employeur"],
                    "name": row["rte_lib_type_employeur"],
                    "measure_id": row["rme_id"],
                    "start_date": start_date,
                    "end_date": end_date,
                },
            }
            records.append(elt)

        self.write_fixture_file(export_path, records)

    def handle(self, dry_run=False, **options):
        self.dry_run = dry_run
        self.set_logger(options.get("verbosity"))

        # Order matters
        self.gen_education_levels()
        self.gen_insee_communes()
        self.gen_insee_departments()
        self.gen_insee_countries()
        self.gen_measures()
        self.gen_employer_types()
