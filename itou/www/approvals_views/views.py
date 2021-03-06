from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.http import FileResponse, Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.template.response import SimpleTemplateResponse
from django.urls import reverse_lazy
from django.utils.text import slugify

from itou.approvals.models import Approval, Suspension
from itou.eligibility.models import EligibilityDiagnosis
from itou.job_applications.models import JobApplication
from itou.utils.pdf import HtmlToPdf
from itou.utils.perms.siae import get_current_siae_or_404
from itou.utils.urls import get_safe_url
from itou.www.approvals_views.forms import DeclareProlongationForm, SuspensionForm


@login_required
def approval_as_pdf(request, job_application_id, template_name="approvals/approval_as_pdf.html"):

    siae = get_current_siae_or_404(request)

    queryset = JobApplication.objects.select_related("job_seeker", "approval", "to_siae")
    job_application = get_object_or_404(queryset, pk=job_application_id, to_siae=siae)

    if not job_application.can_download_approval_as_pdf:
        raise Http404(
            (
                """
            Nous sommes au regret de vous informer que
            vous ne pouvez pas télécharger cet agrément."""
            )
        )

    approval = job_application.approval

    diagnosis = None
    diagnosis_author = None
    diagnosis_author_org = None
    diagnosis_author_org_name = None

    # If an approval has been delivered by Pole Emploi, a diagnosis might
    # exist in the real world but not in our database.
    # Raise an error only if the diagnosis does not exist for an Itou approval.
    if approval.originates_from_itou:
        if approval.is_valid:
            diagnosis = EligibilityDiagnosis.objects.last_considered_valid(
                job_application.job_seeker, for_siae=job_application.to_siae
            )
        else:
            # The PDF should be downloadable even when the PASS IAE has expired.
            # In this case, we have to find a diagnosis made before the pass expires.
            diagnosis = EligibilityDiagnosis.objects.last_before(
                job_application.job_seeker, before_date=approval.end_at, for_siae=job_application.to_siae
            )
        if not diagnosis:
            raise ObjectDoesNotExist
        diagnosis_author = diagnosis.author.get_full_name()
        diagnosis_author_org = diagnosis.author_prescriber_organization or diagnosis.author_siae
        if diagnosis_author_org:
            diagnosis_author_org_name = diagnosis_author_org.display_name

    # The PDFShift API can load styles only if it has the full URL.
    base_url = request.build_absolute_uri("/")[:-1]

    if settings.DEBUG:
        # Use staging or production styles when working locally
        # as PDF shift can't access local files.
        base_url = f"{settings.ITOU_PROTOCOL}://{settings.ITOU_STAGING_DN}"

    context = {
        "approval": job_application.approval,
        "base_url": base_url,
        "assistance_url": settings.ITOU_ASSISTANCE_URL,
        "diagnosis_author": diagnosis_author,
        "diagnosis_author_org_name": diagnosis_author_org_name,
        "siae": job_application.to_siae,
        "job_seeker": job_application.job_seeker,
    }

    html = SimpleTemplateResponse(template=template_name, context=context).rendered_content

    full_name_slug = slugify(job_application.job_seeker.get_full_name())
    filename = f"{full_name_slug}-pass-iae.pdf"

    with HtmlToPdf(html, autoclose=False) as transformer:
        return FileResponse(transformer.file, as_attachment=True, filename=filename)


@login_required
def declare_prolongation(request, approval_id, template_name="approvals/declare_prolongation.html"):
    """
    Declare a prolongation for the given approval.
    """

    siae = get_current_siae_or_404(request)
    approval = get_object_or_404(Approval, pk=approval_id)

    if not approval.can_be_prolonged_by_siae(siae):
        raise PermissionDenied()

    back_url = get_safe_url(request, "back_url", fallback_url=reverse_lazy("dashboard:index"))
    preview = False

    form = DeclareProlongationForm(approval=approval, siae=siae, data=request.POST or None)

    if request.method == "POST" and form.is_valid():

        prolongation = form.save(commit=False)
        prolongation.created_by = request.user
        prolongation.declared_by = request.user
        prolongation.declared_by_siae = form.siae
        prolongation.validated_by = form.validated_by

        if request.POST.get("edit"):
            preview = False
        if request.POST.get("preview"):
            preview = True
        elif request.POST.get("save"):
            prolongation.save()
            # Send an email w/o DB changes
            prolongation.notify_authorized_prescriber()
            messages.success(request, "Déclaration de prolongation enregistrée.")
            return HttpResponseRedirect(back_url)

    context = {
        "approval": approval,
        "back_url": back_url,
        "form": form,
        "preview": preview,
    }
    return render(request, template_name, context)


@login_required
def suspend(request, approval_id, template_name="approvals/suspend.html"):
    """
    Suspend the given approval.
    """

    siae = get_current_siae_or_404(request)
    approval = get_object_or_404(Approval, pk=approval_id)

    if not approval.can_be_suspended_by_siae(siae):
        raise PermissionDenied()

    back_url = get_safe_url(request, "back_url", fallback_url=reverse_lazy("dashboard:index"))
    preview = False

    form = SuspensionForm(approval=approval, siae=siae, data=request.POST or None)

    if request.method == "POST" and form.is_valid():

        suspension = form.save(commit=False)
        suspension.created_by = request.user

        if request.POST.get("edit"):
            preview = False
        if request.POST.get("preview"):
            preview = True
        elif request.POST.get("save"):
            suspension.save()
            messages.success(request, "Suspension effectuée.")
            return HttpResponseRedirect(back_url)

    context = {
        "approval": approval,
        "back_url": back_url,
        "form": form,
        "preview": preview,
    }
    return render(request, template_name, context)


@login_required
def suspension_update(request, suspension_id, template_name="approvals/suspension_update.html"):
    """
    Edit the given suspension.
    """

    siae = get_current_siae_or_404(request)
    suspension = get_object_or_404(Suspension, pk=suspension_id)

    if not suspension.can_be_handled_by_siae(siae):
        raise PermissionDenied()

    back_url = get_safe_url(request, "back_url", fallback_url=reverse_lazy("dashboard:index"))

    form = SuspensionForm(approval=suspension.approval, siae=siae, instance=suspension, data=request.POST or None)

    if request.method == "POST" and form.is_valid():
        suspension = form.save(commit=False)
        suspension.updated_by = request.user
        suspension.save()
        messages.success(request, "Modification de suspension effectuée.")
        return HttpResponseRedirect(back_url)

    context = {
        "suspension": suspension,
        "back_url": back_url,
        "form": form,
    }
    return render(request, template_name, context)


@login_required
def suspension_delete(request, suspension_id, template_name="approvals/suspension_delete.html"):
    """
    Delete the given suspension.
    """

    siae = get_current_siae_or_404(request)
    suspension = get_object_or_404(Suspension, pk=suspension_id)

    if not suspension.can_be_handled_by_siae(siae):
        raise PermissionDenied()

    back_url = get_safe_url(request, "back_url", fallback_url=reverse_lazy("dashboard:index"))

    if request.method == "POST" and request.POST.get("confirm") == "true":
        suspension.delete()
        messages.success(request, "Annulation de suspension effectuée.")
        return HttpResponseRedirect(back_url)

    context = {
        "suspension": suspension,
        "back_url": back_url,
    }
    return render(request, template_name, context)
