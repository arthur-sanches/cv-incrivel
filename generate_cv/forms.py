from django import forms


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
