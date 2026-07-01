from django import forms
from resume.models import Resume


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Resume
        fields = [
            "summary",
            "work_experiences",
            "skills",
            "education",
            "certificates",
            "languages",
            "links",
        ]
        widgets = {
            "summary": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Brief professional summary...",
                }
            ),
            "work_experiences": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 6,
                    "placeholder": "List your work experiences...",
                }
            ),
            "skills": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "e.g. Python, Django, JavaScript...",
                }
            ),
            "education": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Your educational background...",
                }
            ),
            "certificates": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Relevant certificates...",
                }
            ),
            "languages": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "e.g. English (Fluent), Spanish (Native)...",
                }
            ),
            "links": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "e.g. LinkedIn, GitHub, portfolio...",
                }
            ),
        }
        labels = {
            "summary": "Professional Summary",
            "work_experiences": "Work Experiences",
            "skills": "Skills",
            "education": "Education",
            "certificates": "Certificates",
            "languages": "Languages",
            "links": "Links",
        }
        help_texts = {
            "work_experiences": "One experience per block. Include role, company, duration, and description.",
            "skills": "Separate skills with commas or list them line by line.",
            "education": "Include degree, institution, and graduation year.",
            "certificates": "One certificate per line.",
            "languages": "One language per line with proficiency level.",
            "links": "One link per line.",
        }
