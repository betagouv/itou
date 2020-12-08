from django.db import models
from django.forms import ValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from itou.approvals.models import Approval
from itou.eligibility.models import EligibilityDiagnosis
from itou.siae.models import FinancialAnnex
from itou.siaes.models import Siae
from itou.users.models import User
from itou.utils.validators import validate_siret


# INSEE codes
# Are needed for:
# - the current living address of the employee
# - the birth place of the employee


class PeriodMixinQuerySet(models.QuerySet):
    def current(self):
        return self.filter(end_date=None)


class PeriodMixin(models.Model):
    start_date = models.DateField(verbose_name=_("Début de validité"))
    end_date = models.DateField(verbose_name=_("Fin de validité"), null=True)

    class Meta:
        abstract = True


class INSEECommune(PeriodMixin):
    """
    INSEE commune

    Code and name of French communes.
    Mainly used to get the commune code (different from postal code).

    Imported from ASP reference file: ref_insee_com_v1.csv

    Note:
    reference file is currently not up-to-date (2018)
    """

    code = models.Charfield(max_length=5, verbose_name=_("Code commune INSEE"))
    name = models.CharField(max_length=50, verbose_name=_("Nom de la commune"))

    def __str__(self):
        return f"{self.code} - {self.name}"

    def __repr__(self):
        return f"INSEE:code={self.code}, name={self.name}"


class INSEEDepartment(PeriodMixin):
    """
    INSEE department code

    Code and name of French departments

    Imported from ASP reference file: ref_insee_dpt_v2.csv
    """

    code = models.CharField(max_length=3, verbose_name=_("Code département INSEE"))
    name = models.CharField(max_length=50, verbose_name=_("Nom du département"))

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"INSEEDepartementCode:code={self.code}, name={self.name}"


class INSEECountry(models.Model):
    """
    INSEE country code

    Code and name of world countries

    Imported from ASP reference file: ref_insee_pays_v4.csv
    """

    COUNTRY_GROUP_FRANCE = "1"
    # CEE = "Communauté Economique Européenne" is not used since 1993...
    COUNTRY_GROUP_CEE = "2"
    COUNTRY_GROUP_NOT_CEE = "3"

    COUNTRY_GROUP_CHOICES = (
        (COUNTRY_GROUP_FRANCE, _("France")),
        (COUNTRY_GROUP_CEE, _("CEE"), (COUNTRY_GROUP_NOT_CEE, _("Hors CEE"))),
    )

    code = models.CharField(max_length=3, verbose_name=_("Code pays INSEE"))
    name = models.CharField(max_length=50, verbose_name=_("Nom du pays"))
    group = models.CharField(max_length=1, choices=COUNTRY_GROUP_CHOICES)
    # TODO DPT field ?

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"INSEECountry:code={self.code}, name={self.name}"


class EducationalLevel(PeriodMixin):
    """
    Educational level of the employee

    Imported from ASP reference file: ref_niveau_formation_v3.csv
    """

    code = models.CharField(max_length=2, verbose_name=_("Code niveau de formation"))
    name = models.CharField(max_length=100, verbose_name=_("Nom du niveau de formation"))

    # TODO rme_id field used ?


class EmployeeRecordQuerySet(models.QuerySet):
    pass


class EmployeeRecord(models.Model):
    """
    EmployeeRecord - Fiche salarié

    Holds information needed for JSON exports of "fiches salariés" to ASP
    """

    # EmployeeRecord is only available for these kind of SIAE
    KIND_EI = "EI"
    KIND_ACI = "ACI"
    KIND_ETTI = "ETTI"

    KIND_CHOICES = (
        (KIND_EI, _("Entreprise d'insertion")),
        (KIND_ACI, _("Atelier chantier d'insertion")),
        (KIND_ETTI, _("Entreprise de travail temporaire d'insertion")),
    )

    # Current possible statuses for an EmployeeRecord (WIP?)
    STATUS_NEW = "NEW"
    STATUS_COMPLETE = "COMPLETE"
    STATUS_SENT = "SENT"
    STATUS_REFUSED = "REFUSED"
    STATUS_PROCESSED = "PROCESSED"

    STATUS_CHOICES = (
        (STATUS_NEW, _("Nouvelle fiche salarié")),
        (STATUS_COMPLETE, _("Données complètes")),
        (STATUS_SENT, _("Envoyée ASP")),
        (STATUS_REFUSED, _("Rejet ASP")),
        (STATUS_PROCESSED, _("Traitée ASP")),
    )

    # TODO move to eligibility diagnosis
    ALLOCATION_DURATION_NONE = "NONE"
    ALLOCATION_DURATION_LT_6_MONTHS = "NONE"
    ALLOCATION_DURATION_6_TO_11_MONTHS = "NONE"
    ALLOCATION_DURATION_12_TO_23_MONTHS = "NONE"
    ALLOCATION_DURATION_GT_24_MONTHS = "NONE"

    ALLOCATION_DURATION_CHOICES = (
        (ALLOCATION_DURATION_NONE, _("Aucune")),
        (ALLOCATION_DURATION_LT_6_MONTHS, _("Moins de 6 mois")),
        (ALLOCATION_DURATION_6_TO_11_MONTHS, _("De 6 à 11 mois")),
        (ALLOCATION_DURATION_12_TO_23_MONTHS, _("De 12 à 23 mois")),
        (ALLOCATION_DURATION_GT_24_MONTHS, _("24 mois et plus")),
    )

    # ..

    siret = models.CharField(verbose_name=_("Siret"), max_length=14, validators=[validate_siret])

    # kind:
    # kept the same name as in SIAE and prescriber models.
    # The kind of a structure is refered as "mesure" for ASP
    kind = models.CharField(verbose_name=_("Type"), max_length=4, choices=KIND_CHOICES)

    # status:
    # Employee record cycle of life:
    # - New: newly created
    # - Complete: all required fields are present to generate a JSON outpout
    # - Sent: When complete, JSON export can be sent to ASP
    # - Refused: For any reason reject by ASP, can be updated and submited again
    # - Processed: Sent to ASP and got positive feedback of processing by ASP. Can not be changed anymore
    status = models.CharField(verbose_name=_("Etat"), max_length=10, choices=STATUS_CHOICES, default=STATUS_NEW)

    # TODO Store refusal reason from ASP ?

    # json:
    # Once the employee record has reached its final state (TBD), it can't be updated.
    # However related / linked objects live their lives and are subject to changes.
    # The json field is an immutable representation of the employee record actually
    # sent to ASP and act as proof.
    json = models.JSONField(verbose_name=_("Fiche salarié (JSON)"), null=True)
    process_response = models.JSONField(verbose_name=_("Réponse traitement ASP"))

    created_at = models.DateTimeField(verbose_name=_("Date de création"), default=timezone.now)
    updated_at = models.DateTimeField(verbose_name=_("Date de modification"), null=True)

    # Link to financial annex, mainlu for its number
    financial_annex = models.ForeignKey(FinancialAnnex, on_delete=models.CASCADE)

    # Some information in the eligibility diagnosis can be used in the ER
    eligibility_diagnosis = models.ForeignKey(EligibilityDiagnosis, on_delete=models.CASCADE)

    # Link the approval, mainly for its number
    approval = models.ForeignKey(Approval, on_delete=models.CASCADE)

    # Employee
    # ---
    # An employee / User currently have the following needed information:
    # -
    # - personnePhysique.passIae: if user has a valid PASS IAE
    # - personnePhysique.dateNaissance
    # - personnePhysique.idItou: will be generated
    # - personnePhysique.prenom
    # - personnePhysique.prenom
    # Most information of the "adresse" part of the JSON ER can also befound in User model:
    # - adresse.adrTelephone: user.
    # - adresse.adrMail
    # - adresse.codepostalcedex
    # Not captured yet:
    # - personnePhysique.civilite
    # - personnePhysique.nomNaissance
    # - personnePhysique.codeComInsee.codeComInsee
    # - personnePhysique.codeComInsee.codeDpt
    employee = models.ForeignKey(User, verbose_name=_("Employé"), on_delete=models.CASCADE)
    educational_leval = models.ForeignKey(EducationalLevel, verbose_name=("Niveau de formation"))
    birth_place = models.ForeignKey(INSEECommune, verbose_name=_("Commune de naissance"))
    birth_country = models.ForeignKey(INSEECountry, verbose_name=_("Pays de naissance"))

    # birth_place = models.ForeignKey(INSEECode, verbose_name=_("Lieu de naissance"))

    class Meta:
        verbose_name = _("Fiche salarié")
        # An Employee record is unique for a given SIRET and Approval (number)
        unique_together = ("siret", "approval")

    def __str__(self):
        return f"EmployeeRecord:SIRET={self.siret},PASS-IAE={self.approval.number}"

    def clean(self):
        # Employee record can't be updated anymore if in "final" status
        if not self.is_updatable:
            raise ValidationError(_("Cette fiche salarié est historisée et non-modifiable"))
        return super.clean()

    def save(self, *args, **kwargs):
        # When not using a form for updating / creating EmployeeRecord objects
        # performing a clean on the model will ensure some constraints are checked
        self.clean()
        if self.pk:
            self.updated_at = timezone.now()
        return super.save(*args, **kwargs)

    @property
    def is_updatable(self):
        """
        Once in final state (PROCESSED), an EmployeeRecord is not updatable anymore.
        See model save() and clean() method.
        """
        return not (self.status == self.kind.STATUS_PROCESSED and self.json is not None)

    @property
    def set_complete(self):
        pass

    @staticmethod
    def convert_kind_to_asp_id(kind):
        """
        Conversion of Siae.kind field value to ASP employer type  
        i.e. field `rte_code_type_employeur` of ASP reference file: ref_type_employeur_v3.csv 

        Employer code is coded in one char.

        ASP has a code 5 for ESAT (not used)
        """
        if kind == Siae.KIND_EI:
            return "1"
        elif kind == Siae.KIND_ETTI:
            return "2"
        elif kind == Siae.KIND_AI:
            return "3"
        elif kind == Siae.KIND_ACI:
            return "4"
        elif kind == Siae.KIND_EA:
            return "6"
        else:
            return "7"  # Other / "Autres"
