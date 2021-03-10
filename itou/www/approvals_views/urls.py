from django.urls import path

from itou.www.approvals_views import views


# https://docs.djangoproject.com/en/dev/topics/http/urls/#url-namespaces-and-included-urlconfs
app_name = "approvals"

urlpatterns = [
    path("download/<uuid:job_application_id>", views.approval_as_pdf, name="approval_as_pdf"),
    path("request_prolongation/<int:approval_id>", views.request_prolongation, name="request_prolongation"),
    path("suspend/<int:approval_id>", views.suspend, name="suspend"),
    path("suspension/<int:suspension_id>/edit", views.suspension_update, name="suspension_update"),
    path("suspension/<int:suspension_id>/delete", views.suspension_delete, name="suspension_delete"),
]
