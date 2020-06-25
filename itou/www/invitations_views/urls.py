from django.urls import path

from itou.www.invitations_views import views


# https://docs.djangoproject.com/en/dev/topics/http/urls/#url-namespaces-and-included-urlconfs
app_name = "invitations_views"

urlpatterns = [
    path("invite_siae_staff", views.invite_siae_staff, name="invite_siae_staff"),
    path("<str:invitation_type>/<uuid:invitation_id>/new_user", views.new_user, name="new_user"),
    path("<uuid:invitation_id>/join_siae", views.join_siae, name="join_siae"),
]
