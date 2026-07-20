from django import forms
from django.core.exceptions import ValidationError

import json


class GenerateCvForm(forms.Form):
    job_description = forms.CharField(
        label="Job Description",
        required=True,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "placeholder": "Paste the job description here...",
                "rows": 10,
                "style": "resize: vertical;",
            }
        ),
    )


class CvDownloadForm(forms.Form):
    name = forms.CharField(
        label="File Name",
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "e.g. My Tailored CV",
            }
        ),
    )


class EditGeneratedCVForm(forms.Form):
    name = forms.CharField(
        label="CV Name",
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "e.g. My Tailored CV",
            }
        ),
    )
    professional_summary = forms.CharField(
        label="Professional Summary",
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 6,
                "style": "resize: vertical;",
            }
        ),
    )
    work_experiences = forms.CharField(
        label="Work Experiences (JSON)",
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 8,
                "style": "resize: vertical; font-family: monospace;",
            }
        ),
    )
    skills = forms.CharField(
        label="Skills (JSON)",
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 6,
                "style": "resize: vertical; font-family: monospace;",
            }
        ),
    )
    education = forms.CharField(
        label="Education (JSON)",
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 6,
                "style": "resize: vertical; font-family: monospace;",
            }
        ),
    )
    certificates = forms.CharField(
        label="Certificates (JSON)",
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 4,
                "style": "resize: vertical; font-family: monospace;",
            }
        ),
    )
    languages = forms.CharField(
        label="Languages (JSON)",
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 4,
                "style": "resize: vertical; font-family: monospace;",
            }
        ),
    )
    links = forms.CharField(
        label="Links (JSON)",
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 4,
                "style": "resize: vertical; font-family: monospace;",
            }
        ),
    )
    headings = forms.CharField(
        label="Headings (JSON)",
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 6,
                "style": "resize: vertical; font-family: monospace;",
            }
        ),
    )

    def clean_work_experiences(self):
        return self._validate_json("work_experiences")

    def clean_skills(self):
        return self._validate_json("skills")

    def clean_education(self):
        return self._validate_json("education")

    def clean_certificates(self):
        return self._validate_json("certificates")

    def clean_languages(self):
        return self._validate_json("languages")

    def clean_links(self):
        return self._validate_json("links")

    def clean_headings(self):
        return self._validate_json("headings")

    def _validate_json(self, field_name):
        value = self.cleaned_data.get(field_name, "")
        if not value or not value.strip():
            return ""
        try:
            parsed = json.loads(value)
            return json.dumps(parsed, indent=2)
        except json.JSONDecodeError:
            raise ValidationError(f"Invalid JSON in {field_name}.")
