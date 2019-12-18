from django.contrib import admin

from itou.approvals import models


@admin.register(models.Approval)
class ApprovalAdmin(admin.ModelAdmin):
    list_display = ("id", "number", "user", "start_at", "end_at")
    list_display_links = ("id", "number")
    raw_id_fields = ("user", "created_by")
    readonly_fields = ("created_at", "created_by")

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def add_view(self, request, form_url="", extra_context=None):
        # Prepopulate the form with calculated data.
        g = request.GET.copy()
        g.update({"number": self.model.get_next_number()})
        request.GET = g
        return super().add_view(request, form_url, extra_context=extra_context)
