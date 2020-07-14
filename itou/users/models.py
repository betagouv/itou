from allauth.utils import generate_unique_username
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from itou.approvals.models import ApprovalsWrapper
from itou.utils.address.departments import department_from_postcode
from itou.utils.address.models import AddressMixin
from itou.utils.validators import validate_birthdate, validate_pole_emploi_id


class User(AbstractUser, AddressMixin):
    """
    Custom user model.

    Default fields are listed here:
    https://github.com/django/django/blob/972eef6b9060aee4a092bedee38a7775fbbe5d0b/django/contrib/auth/models.py#L289

    Auth is managed with django-allauth.

    To retrieve SIAEs this user belongs to:
        self.siae_set.all()
        self.siaemembership_set.all()

    To retrieve prescribers this user belongs to:
        self.prescriberorganization_set.all()
        self.prescribermembership_set.all()
    """

    REASON_FORGOTTEN = "FORGOTTEN"
    REASON_NOT_REGISTERED = "NOT_REGISTERED"
    REASON_CHOICES = (
        (REASON_FORGOTTEN, _("Identifiant Pôle emploi oublié")),
        (REASON_NOT_REGISTERED, _("Non inscrit auprès de Pôle emploi")),
    )

    ERROR_EMAIL_ALREADY_EXISTS = _(f"Cet e-mail existe déjà.")

    birthdate = models.DateField(
        verbose_name=_("Date de naissance"), null=True, blank=True, validators=[validate_birthdate]
    )
    phone = models.CharField(verbose_name=_("Téléphone"), max_length=20, blank=True)

    is_job_seeker = models.BooleanField(verbose_name=_("Demandeur d'emploi"), default=False)
    is_prescriber = models.BooleanField(verbose_name=_("Prescripteur"), default=False)
    is_siae_staff = models.BooleanField(verbose_name=_("Employeur (SIAE)"), default=False)

    # The two following Pôle emploi fields are reserved for job seekers.
    # They are used in the process of delivering an approval.
    # They depend on each other: one or the other must be filled but not both.

    # Pôle emploi ID is not guaranteed to be unique.
    # At least, we haven't received any confirmation of its uniqueness.
    # It looks like it pre-dates the national merger and may be unique
    # by user and by region…
    pole_emploi_id = models.CharField(
        verbose_name=_("Identifiant Pôle emploi"),
        help_text=_("7 chiffres suivis d'une 1 lettre ou d'un chiffre."),
        max_length=8,
        validators=[validate_pole_emploi_id, MinLengthValidator(8)],
        blank=True,
    )
    lack_of_pole_emploi_id_reason = models.CharField(
        verbose_name=_("Pas d'identifiant Pôle emploi ?"),
        help_text=_("Indiquez la raison de l'absence d'identifiant Pôle emploi."),
        max_length=30,
        choices=REASON_CHOICES,
        blank=True,
    )

    resume_link = models.URLField(max_length=500, verbose_name=_("Lien vers un CV"), null=True)

    created_by = models.ForeignKey(
        "self", verbose_name=_("Créé par"), on_delete=models.SET_NULL, null=True, blank=True
    )

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        already_exists = bool(self.pk)
        # There is no unicity constraint on `email` at the DB level.
        # It's in anticipation of other authentication methods to
        # authenticate against something else, e.g. username/password.
        if not already_exists and hasattr(self, "email") and User.email_already_exists(self.email):
            raise ValidationError(self.ERROR_EMAIL_ALREADY_EXISTS)

        # Update department from postal code (if possible)
        self.department = department_from_postcode(self.post_code)

        super().save(*args, **kwargs)

    @property
    def approvals_wrapper(self):
        if not self.is_job_seeker:
            return None
        return ApprovalsWrapper(self)

    @property
    def has_eligibility_diagnosis(self):
        """
        Returns True if a diagnosis exists, False otherwise.
        """
        if not self.is_job_seeker:
            return False
        if self.eligibility_diagnoses.exists():
            return True
        # The existence of a valid `PoleEmploiApproval` implies that a diagnosis
        # has been made outside of Itou.
        latest_approval = self.approvals_wrapper.latest_approval
        return latest_approval and latest_approval.is_valid and not latest_approval.originates_from_itou

    def get_eligibility_diagnosis(self):
        if not self.is_job_seeker:
            return None
        return self.eligibility_diagnoses.select_related(
            "author", "author_siae", "author_prescriber_organization"
        ).latest("-created_at")

    @cached_property
    def is_peamu(self):
        social_accounts = self.socialaccount_set.all()
        # We have to do all this in python to benefit from prefetch_related.
        return len([sa for sa in social_accounts if sa.provider == "peamu"]) >= 1

    @cached_property
    def peamu_id_token(self):
        if not self.is_peamu:
            return None
        return self.socialaccount_set.filter(provider="peamu").get().extra_data["id_token"]

    @classmethod
    def create_job_seeker_by_proxy(cls, proxy_user, **fields):
        """
        Used when a "prescriber" user creates another user of kind "job seeker".

        Minimum required keys in `fields` are:
            {
                "email": "foo@foo.com",
                "first_name": "Foo",
                "last_name": "Foo",
            }
        """
        username = generate_unique_username([fields["first_name"], fields["last_name"], fields["email"]])
        fields["is_job_seeker"] = True
        fields["created_by"] = proxy_user
        user = cls.objects.create_user(
            username, email=fields.pop("email"), password=cls.objects.make_random_password(), **fields
        )
        return user

    @classmethod
    def email_already_exists(cls, email):
        """
        RFC 5321 Part 2.4 states that only the domain portion of an email
        is case-insensitive. Consider toto@toto.com and TOTO@toto.com as
        the same email.
        """
        return cls.objects.filter(email__iexact=email).exists()

    @staticmethod
    def clean_pole_emploi_fields(pole_emploi_id, lack_of_pole_emploi_id_reason):
        """
        Only for users with the `is_job_seeker` flag set to True.
        Validate Pôle emploi fields that depend on each other: one or
        the other must be filled but not both.
        It must be used in forms and modelforms that manipulate job seekers.
        """
        if (pole_emploi_id and lack_of_pole_emploi_id_reason) or (
            not pole_emploi_id and not lack_of_pole_emploi_id_reason
        ):
            raise ValidationError(_("Renseignez soit un identifiant Pôle emploi, soit la raison de son absence."))

    @property
    def is_prescriber_with_org(self):
        return self.is_prescriber and self.prescriberorganization_set.exists()


def get_allauth_account_user_display(user):
    return user.email
