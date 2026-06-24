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
