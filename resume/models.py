from django.db import models
from django.conf import settings


class Resume(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="resume",
    )
    name = models.CharField(
        verbose_name="Full Name",
        max_length=255,
        blank=True,
        default="",
    )
    contact_email = models.EmailField(
        verbose_name="Contact Email",
        max_length=255,
        blank=True,
        default="",
    )
    phone = models.CharField(
        verbose_name="Phone",
        max_length=50,
        blank=True,
        default="",
    )
    address = models.CharField(
        verbose_name="Address",
        max_length=500,
        blank=True,
        default="",
    )
    summary = models.TextField(
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
        return f"Resume #{self.pk} - {self.user}"
