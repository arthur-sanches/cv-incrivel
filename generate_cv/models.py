from django.db import models
from django.conf import settings


class GeneratedCV(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="generated_cvs",
    )
    professional_summary = models.TextField(
        verbose_name="Professional Summary",
        blank=True,
        default="",
    )
    work_experiences = models.TextField(
        verbose_name="Work Experiences",
        blank=True,
        default="",
    )
    skills = models.TextField(
        verbose_name="Skills",
        blank=True,
        default="",
    )
    education = models.TextField(
        verbose_name="Education",
        blank=True,
        default="",
    )
    certificates = models.TextField(
        verbose_name="Certificates",
        blank=True,
        default="",
    )
    languages = models.TextField(
        verbose_name="Languages",
        blank=True,
        default="",
    )
    links = models.TextField(
        verbose_name="Links",
        blank=True,
        default="",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"GeneratedCV #{self.pk} - {self.user}"
