from django.contrib import admin

from .models import Resume


@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ("user", "created_at", "updated_at")
    list_filter = ("created_at",)
    search_fields = ("user__email", "summary", "skills")
    readonly_fields = ("created_at", "updated_at")
