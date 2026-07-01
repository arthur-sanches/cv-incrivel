from django import forms


class ResumeUploadForm(forms.Form):
    file = forms.FileField(
        label="Upload your resume",
        help_text="Accepted formats: .docx, .pdf",
    )

    def clean_file(self):
        file = self.cleaned_data["file"]
        if not file.name.lower().endswith((".docx", ".pdf")):
            raise forms.ValidationError("Only .docx and .pdf files are accepted.")
        return file


class PersonalInfoForm(forms.Form):
    name = forms.CharField(
        label="Full Name",
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. John Doe"}),
    )
    email = forms.EmailField(
        label="Email",
        max_length=255,
        required=True,
        widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "e.g. john@example.com"}),
    )
    phone = forms.CharField(
        label="Phone",
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. +1 (555) 123-4567"}),
    )
    address = forms.CharField(
        label="Address",
        max_length=500,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. 123 Main St, City (optional)"}),
    )
