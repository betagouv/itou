from allauth.account.adapter import get_adapter
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.utils import formats, safestring
from django.utils.translation import gettext as _, ngettext as __

from itou.invitations.models import InvitationAbstract, PrescriberWithOrgInvitation, SiaeStaffInvitation
from itou.users.models import User
from itou.utils.perms.prescriber import get_current_org_or_404
from itou.utils.perms.siae import get_current_siae_or_404
from itou.utils.urls import get_safe_url
from itou.www.invitations_views.forms import (
    NewPrescriberWithOrgInvitationFormSet,
    NewSiaeStaffInvitationFormSet,
    NewUserForm,
)


def new_user(request, invitation_type, invitation_id, template_name="invitations_views/new_user.html"):
    invitation_type = InvitationAbstract.get_model_from_string(invitation_type)
    invitation = get_object_or_404(invitation_type, pk=invitation_id)
    context = {"invitation": invitation}
    next_step = None

    if request.user.is_authenticated:
        if not request.user.email == invitation.email:
            message = (
                "Un utilisateur est déjà connecté.<br>"
                "Merci de déconnecter ce compte en cliquant sur le bouton ci-dessous. "
                "La page d'accueil se chargera automatiquement, n'en tenez pas compte.<br>"
                "Retournez dans votre boite mail et cliquez de nouveau sur le lien "
                "reçu pour accepter l'invitation."
            )
            message = safestring.mark_safe(message)
            messages.error(request, _(message))
            return redirect("account_logout")

    if invitation.can_be_accepted:
        user = User.objects.filter(email__iexact=invitation.email)
        if user:
            # The user exists but he should log in first
            next_step = "{}?account_type={}&next={}".format(
                reverse("account_login"), invitation.SIGNIN_ACCOUNT_TYPE, get_safe_url(request, "redirect_to")
            )
            next_step = redirect(next_step)
        else:
            # A new user should be created before joining
            form = NewUserForm(data=request.POST or None, invitation=invitation)
            context["form"] = form
            if form.is_valid():
                user = form.save(request)
                get_adapter().login(request, user)
                next_step = redirect(get_safe_url(request, "redirect_to"))
    else:
        messages.error(request, _("Cette invitation n'est plus valide."))

    return next_step or render(request, template_name, context=context)


@login_required
def invite_prescriber_with_org(request, template_name="invitations_views/create.html"):
    organization = get_current_org_or_404(request)
    form_kwargs = {"sender": request.user, "organization": organization}
    formset = NewPrescriberWithOrgInvitationFormSet(data=request.POST or None, form_kwargs=form_kwargs)
    if request.POST:
        if formset.is_valid():
            invitations = formset.save()

            for invitation in invitations:
                invitation.send()

            count = len(formset.forms)
            message_singular = (
                "Votre invitation a été envoyée par courriel.<br>"
                "Pour rejoindre votre organisation, il suffira simplement à votre invité(e) "
                "de cliquer sur le lien de validation contenu dans le courriel.<br>"
            )
            message_plural = (
                "Vos invitations ont été envoyées par courriel.<br>"
                "Pour rejoindre votre organisation, il suffira simplement à vos invités "
                "de cliquer sur le lien de validation contenu dans le courriel.<br>"
            )
            message = __(message_singular, message_plural, count) % {"count": count}
            expiration_date = formats.date_format(invitations[0].expiration_date)
            message += _(f"Le lien de validation est valable jusqu'au {expiration_date}.")
            message = safestring.mark_safe(message)
            messages.success(request, message)

            return redirect(request.path)

    form_post_url = reverse("invitations_views:invite_prescriber_with_org")
    back_url = reverse("prescribers_views:members")
    context = {"back_url": back_url, "form_post_url": form_post_url, "formset": formset}

    return render(request, template_name, context)


@login_required
def join_prescriber_organization(request, invitation_id):
    invitation = get_object_or_404(PrescriberWithOrgInvitation, pk=invitation_id)
    if not invitation.guest_can_join_organization(request):
        raise PermissionDenied()

    if invitation.can_be_accepted:
        invitation.add_invited_user_to_organization()
        invitation.accept()
        messages.success(
            request, _(f"Vous êtes désormais membre de l'organisation {invitation.organization.display_name}.")
        )
    else:
        messages.error(request, _("Cette invitation n'est plus valide."))

    return redirect("dashboard:index")


@login_required
def invite_siae_staff(request, template_name="invitations_views/create.html"):
    siae = get_current_siae_or_404(request)
    form_kwargs = {"sender": request.user, "siae": siae}
    formset = NewSiaeStaffInvitationFormSet(data=request.POST or None, form_kwargs=form_kwargs)
    if request.POST:
        if formset.is_valid():
            invitations = formset.save()

            for invitation in invitations:
                invitation.send()

            count = len(formset.forms)
            message_singular = (
                "Votre invitation a été envoyée par e-mail.<br>"
                "Pour rejoindre votre organisation, l'invité(e) peut désormais cliquer "
                "sur le lien de validation reçu dans le courriel.<br>"
            )
            message_plural = (
                "Vos invitations ont été envoyées par e-mail.<br>"
                "Pour rejoindre votre organisation, vos invités peuvent désormais "
                "cliquer sur le lien de validation reçu dans l'e-mail.<br>"
            )
            message = __(message_singular, message_plural, count) % {"count": count}
            expiration_date = formats.date_format(invitations[0].expiration_date)
            message += _(f"Le lien de validation est valable jusqu'au {expiration_date}.")
            message = safestring.mark_safe(message)
            messages.success(request, message)

            return redirect(request.path)

    form_post_url = reverse("invitations_views:invite_siae_staff")
    back_url = reverse("siaes_views:members")
    context = {"back_url": back_url, "form_post_url": form_post_url, "formset": formset}

    return render(request, template_name, context)


@login_required
def join_siae(request, invitation_id):
    invitation = get_object_or_404(SiaeStaffInvitation, pk=invitation_id)
    if not invitation.guest_can_join_siae(request):
        raise PermissionDenied()

    if not invitation.siae.is_active:
        messages.error(request, _("Cette structure n'est plus active."))
    elif invitation.can_be_accepted:
        invitation.add_invited_user_to_siae()
        invitation.accept()
        messages.success(request, _(f"Vous êtes désormais membre de la structure {invitation.siae.display_name}."))
    else:
        messages.error(request, _("Cette invitation n'est plus valide."))

    request.session[settings.ITOU_SESSION_CURRENT_SIAE_KEY] = invitation.siae.pk
    return redirect("dashboard:index")
