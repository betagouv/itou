from django.contrib import admin, messages
from django.contrib.auth import get_permission_codename
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils.translation import gettext as _

from itou.approvals.admin_forms import ManuallyAddApprovalForm, ProlongationForm
from itou.approvals.models import Approval, Prolongation
from itou.job_applications.models import JobApplication, JobApplicationWorkflow
from itou.utils.emails import get_email_text_template


@transaction.atomic
def manually_add_approval(
    request, model_admin, job_application_id, template_name="admin/approvals/manually_add_approval.html"
):
    """
    Custom admin view to manually add an approval.

    https://docs.djangoproject.com/en/dev/ref/contrib/admin/#adding-views-to-admin-sites
    https://github.com/django/django/blob/master/django/contrib/admin/templates/admin/change_form.html
    """

    admin_site = model_admin.admin_site
    opts = model_admin.model._meta
    app_label = opts.app_label
    codename = get_permission_codename("add", opts)
    has_perm = request.user.has_perm(f"{app_label}.{codename}")

    if not has_perm:
        raise PermissionDenied

    queryset = JobApplication.objects.select_related(
        "job_seeker", "sender", "sender_siae", "sender_prescriber_organization", "to_siae"
    )
    job_application = get_object_or_404(
        queryset,
        pk=job_application_id,
        state=JobApplicationWorkflow.STATE_ACCEPTED,
        approval=None,
        approval_manually_refused_at=None,
        approval_manually_refused_by=None,
        approval_number_sent_by_email=False,
    )

    initial = {
        "start_at": job_application.hiring_start_at,
        "end_at": Approval.get_default_end_date(job_application.hiring_start_at),
        "number": Approval.get_next_number(job_application.hiring_start_at),
        "user": job_application.job_seeker.pk,
        "created_by": request.user.pk,
    }
    form = ManuallyAddApprovalForm(initial=initial, data=request.POST or None)
    fieldsets = [(None, {"fields": list(form.base_fields)})]
    adminForm = admin.helpers.AdminForm(form, fieldsets, {})

    if request.method == "POST" and form.is_valid():
        approval = form.save()
        job_application.approval = approval
        job_application.save()
        job_application.manually_deliver_approval(delivered_by=request.user)
        messages.success(
            request, _(f"Le PASS IAE {approval.number_with_spaces} a bien été créé et envoyé par e-mail.")
        )
        return HttpResponseRedirect(reverse("admin:approvals_approval_changelist"))

    context = {
        "add": True,
        "adminform": adminForm,
        "admin_site": admin_site.name,
        "app_label": app_label,
        "errors": admin.helpers.AdminErrorList(form, {}),
        "form": form,
        "job_application": job_application,
        "opts": opts,
        "title": _("Ajout manuel d'un numéro d'agrément"),
        **admin_site.each_context(request),
    }
    return render(request, template_name, context)


@transaction.atomic
def manually_refuse_approval(
    request, model_admin, job_application_id, template_name="admin/approvals/manually_refuse_approval.html"
):
    """
    Custom admin view to manually refuse an approval (in the case of a job seeker in waiting period).
    """

    admin_site = model_admin.admin_site
    opts = model_admin.model._meta
    app_label = opts.app_label
    codename = get_permission_codename("add", opts)
    has_perm = request.user.has_perm(f"{app_label}.{codename}")

    if not has_perm:
        raise PermissionDenied

    queryset = JobApplication.objects.select_related(
        "job_seeker", "sender", "sender_siae", "sender_prescriber_organization", "to_siae"
    )
    job_application = get_object_or_404(
        queryset,
        pk=job_application_id,
        state=JobApplicationWorkflow.STATE_ACCEPTED,
        approval=None,
        approval_manually_delivered_by=None,
        approval_number_sent_by_email=False,
    )

    if request.method == "POST" and request.POST.get("confirm") == "yes":
        job_application.manually_refuse_approval(refused_by=request.user)
        messages.success(request, _("Délivrance du PASS IAE refusée."))
        return HttpResponseRedirect(reverse("admin:approvals_approval_changelist"))

    # Display a preview of the email that will be send.
    email_subject_template = get_email_text_template(
        "approvals/email/refuse_manually_subject.txt", {"job_application": job_application}
    )
    email_body_template = get_email_text_template(
        "approvals/email/refuse_manually_body.txt", {"job_application": job_application}
    )

    context = {
        "add": True,
        "admin_site": admin_site.name,
        "app_label": app_label,
        "email_body_template": email_body_template,
        "email_subject_template": email_subject_template,
        "job_application": job_application,
        "opts": opts,
        "title": _("Confirmer le refus manuel d'un numéro d'agrément"),
        **admin_site.each_context(request),
    }
    return render(request, template_name, context)


@transaction.atomic
def validate_prolongation(
    request, model_admin, prolongation_id, template_name="admin/approvals/prolongation_validate.html"
):
    """
    Custom admin view to validate a prolongation.

    https://docs.djangoproject.com/en/dev/ref/contrib/admin/#adding-views-to-admin-sites
    https://github.com/django/django/blob/master/django/contrib/admin/templates/admin/change_form.html
    """

    admin_site = model_admin.admin_site
    opts = model_admin.model._meta
    app_label = opts.app_label
    codename = get_permission_codename("add", opts)
    has_perm = request.user.has_perm(f"{app_label}.{codename}")

    if not has_perm:
        raise PermissionDenied

    queryset = Prolongation.objects.pending().select_related("approval__user", "siae")
    prolongation = get_object_or_404(queryset, pk=prolongation_id)

    form = ProlongationForm(instance=prolongation, data=request.POST or None)
    fieldsets = [(None, {"fields": list(form.base_fields)})]
    adminForm = admin.helpers.AdminForm(form, fieldsets, {})

    # TODO: handle form submit.

    # Display a preview of the email that will be send.
    context = {"prolongation": prolongation}
    email_subject_template = get_email_text_template("approvals/email/prolongation_validate_subject.txt", context)
    email_body_template = get_email_text_template("approvals/email/prolongation_validate_body.txt", context)

    context = {
        "add": True,
        "adminform": adminForm,
        "admin_site": admin_site.name,
        "app_label": app_label,
        "email_body_template": email_body_template,
        "email_subject_template": email_subject_template,
        "errors": admin.helpers.AdminErrorList(form, {}),
        "form": form,
        "prolongation": prolongation,
        "opts": opts,
        "title": _("Validation d'une prolongation"),
        **admin_site.each_context(request),
    }
    return render(request, template_name, context)


@transaction.atomic
def refuse_prolongation(
    request, model_admin, prolongation_id, template_name="admin/approvals/prolongation_refuse.html"
):
    """
    Custom admin view to refuse a prolongation.

    https://docs.djangoproject.com/en/dev/ref/contrib/admin/#adding-views-to-admin-sites
    https://github.com/django/django/blob/master/django/contrib/admin/templates/admin/change_form.html
    """

    admin_site = model_admin.admin_site
    opts = model_admin.model._meta
    app_label = opts.app_label
    codename = get_permission_codename("add", opts)
    has_perm = request.user.has_perm(f"{app_label}.{codename}")

    if not has_perm:
        raise PermissionDenied

    queryset = Prolongation.objects.pending().select_related("approval__user", "siae")
    prolongation = get_object_or_404(queryset, pk=prolongation_id)

    # TODO: handle form submit.

    # Display a preview of the email that will be send.
    context = {"prolongation": prolongation}
    email_subject_template = get_email_text_template("approvals/email/prolongation_refuse_subject.txt", context)
    email_body_template = get_email_text_template("approvals/email/prolongation_refuse_body.txt", context)

    context = {
        "add": True,
        "admin_site": admin_site.name,
        "app_label": app_label,
        "email_body_template": email_body_template,
        "email_subject_template": email_subject_template,
        "prolongation": prolongation,
        "opts": opts,
        "title": _("Validation d'une prolongation"),
        **admin_site.each_context(request),
    }
    return render(request, template_name, context)
