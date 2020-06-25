from allauth.account.adapter import DefaultAccountAdapter
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.utils import formats, safestring
from django.utils.translation import gettext as _, ngettext as __

from itou.invitations.models import InvitationWrapper, SiaeStaffInvitation
from itou.utils.perms.siae import get_current_siae_or_404
from itou.utils.urls import get_safe_url
from itou.www.invitations_views.forms import NewSiaeStaffInvitationFormSet, NewUserForm


def new_user(request, invitation_type, invitation_id, template_name="invitations_views/new_user.html"):

    invitation_type = InvitationWrapper.get_model_from_string(invitation_type)
    invitation = get_object_or_404(invitation_type, pk=invitation_id)
    context = {"invitation": invitation}
    next_step = None

    if request.user.is_authenticated:
        if not request.user.email == invitation.email:
            messages.error(request, _("Merci de vous déconnecter avant d'accepter cette invitation."))
            return redirect("account_logout")

    if invitation.can_be_accepted:
        user = get_user_model().objects.filter(email=invitation.email)
        if not user:
            form = NewUserForm(data=request.POST or None, invitation=invitation)
            context["form"] = form
            if form.is_valid():
                user = form.save(request)
                DefaultAccountAdapter().login(request, user)
                next_step = redirect(get_safe_url(request, "redirect_to"))
        else:
            next_step = "{}?account_type={}&next={}".format(
                reverse("account_login"), invitation.SIGNIN_ACCOUNT_TYPE, get_safe_url(request, "redirect_to")
            )
            next_step = redirect(next_step)

    return next_step or render(request, template_name, context=context)


@login_required
def join_siae(request, invitation_id, template_name="invitations_views/join_siae.html"):
    invitation = get_object_or_404(SiaeStaffInvitation, pk=invitation_id)
    if not invitation.guest_can_join_organization(request):
        raise PermissionDenied()

    context = {"invitation": invitation, "show_join_button": True}

    next_step = None
    if request.method == "POST":
        if invitation.can_be_accepted:
            invitation.add_invited_user_to_siae()
            invitation.accept()
            messages.success(
                request, _(f"Vous êtes désormais membre de l'organisation {invitation.siae.display_name}.")
            )
            next_step = redirect("dashboard:index")
        else:
            messages.error(request, _("Cette invitation n'est plus valide."))
            context["show_join_button"] = False

    return next_step or render(request, template_name, context=context)


@login_required
def invite_siae_staff(request, template_name="invitations_views/create.html"):
    siae = get_current_siae_or_404(request)
    form_kwargs = {"sender": request.user, "siae": siae}
    formset = NewSiaeStaffInvitationFormSet(data=request.POST or None, form_kwargs=form_kwargs)
    if request.POST:
        if formset.is_valid():
            invitations = formset.save()
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
            formset = NewSiaeStaffInvitationFormSet(form_kwargs=form_kwargs)

    form_post_url = reverse("invitations_views:invite_siae_staff")
    back_url = reverse("siaes_views:members")
    context = {"back_url": back_url, "form_post_url": form_post_url, "formset": formset}

    return render(request, template_name, context)
