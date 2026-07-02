from django import forms
from resume.models import Resume


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Resume
        fields = [
            "name",
            "contact_email",
            "phone",
            "address",
            "summary",
            "work_experiences",
            "skills",
            "education",
            "certificates",
            "languages",
            "links",
        ]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. John Doe",
                }
            ),
            "contact_email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. john@example.com",
                }
            ),
            "phone": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. +1 (555) 123-4567",
                }
            ),
            "address": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. 123 Main St, City (optional)",
                }
            ),
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
            "name": "Full Name",
            "contact_email": "Contact Email",
            "phone": "Phone",
            "address": "Address",
            "summary": "Professional Summary",
            "work_experiences": "Work Experiences",
            "skills": "Skills",
            "education": "Education",
            "certificates": "Certificates",
            "languages": "Languages",
            "links": "Links",
        }
        help_texts = {
            "address": "Optional. Your street address or location.",
            "work_experiences": "One experience per block. Include role, company, duration, and description.",
            "skills": "Separate skills with commas or list them line by line.",
            "education": "Include degree, institution, and graduation year.",
            "certificates": "One certificate per line.",
            "languages": "One language per line with proficiency level.",
            "links": "One link per line.",
        }
