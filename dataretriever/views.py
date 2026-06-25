import re

from django.shortcuts import render

from .forms import ResumeUploadForm, PersonalInfoForm
from .extractors import extract_text_from_docx, extract_text_from_pdf


def index(request):
    extracted_text = None
    error = None
    filename = None
    extraction_done = False
    personal_info_form = PersonalInfoForm()
    redacted_fields = []

    if request.method == "POST":
        form = ResumeUploadForm(request.POST, request.FILES)
        personal_info_form = PersonalInfoForm(request.POST)
        if form.is_valid():
            uploaded_file = request.FILES["file"]
            filename = uploaded_file.name
            file_bytes = uploaded_file.read()
            extraction_done = True

            # Collect personal info for redaction if valid
            sensitive_values = []
            if personal_info_form.is_valid():
                for field in ["name", "email", "phone", "address"]:
                    val = personal_info_form.cleaned_data.get(field, "").strip()
                    if val:
                        sensitive_values.append((val, field.upper()))
                        redacted_fields.append(field)
            # Sort by length descending so longer strings match first
            sensitive_values.sort(key=lambda x: len(x[0]), reverse=True)

            try:
                if filename.lower().endswith(".docx"):
                    extracted_text = extract_text_from_docx(file_bytes)
                elif filename.lower().endswith(".pdf"):
                    extracted_text = extract_text_from_pdf(file_bytes)
                else:
                    error = "Unsupported file format."

                # Redact sensitive data from extracted text
                if extracted_text and sensitive_values:
                    for value, field_name in sensitive_values:
                        extracted_text = re.sub(
                            re.escape(value),
                            f"[REDACTED_{field_name}]",
                            extracted_text,
                            flags=re.IGNORECASE,
                        )
            except Exception as e:
                ext = filename.lower().split(".")[-1] if "." in filename else ""
                suggestion = ""
                if ext == "docx":
                    suggestion = " Try uploading the file as a PDF instead."
                elif ext == "pdf":
                    suggestion = " Try uploading the file as a DOCX instead."
                error = f"Failed to extract text: {str(e)}.{suggestion}"
    else:
        form = ResumeUploadForm()

    return render(
        request,
        "dataretriever/upload.html",
        {
            "form": form,
            "personal_info_form": personal_info_form,
            "extracted_text": extracted_text,
            "error": error,
            "filename": filename,
            "extraction_done": extraction_done,
            "redacted_fields": redacted_fields,
        },
    )
