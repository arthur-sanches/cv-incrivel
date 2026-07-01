import json
import re

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import ResumeUploadForm, PersonalInfoForm
from .extractors import extract_text_from_docx, extract_text_from_pdf
from .models import Resume
from ai_integration.services import OpenRouterClient


def _make_flexible_phone_pattern(phone_value: str) -> str | None:
    """Build a regex that matches phone digits regardless of formatting.

    Extracts only digits from the user-provided value and creates a pattern
    that allows any non-digit characters (spaces, parentheses, dashes, etc.)
    between each digit. Common formatting characters (``(``, ``)``, ``-``,
    ``+``, ``.``, space) are also allowed *before* the first digit and
    *after* the last digit so that e.g. ``(11) 98765-1234`` is fully
    captured when the user entered ``11 98765-1234``.
    """
    digits = re.sub(r"\D", "", phone_value)
    if not digits:
        return None
    # Allow any non-digit characters between consecutive digits
    inner = r"\D*".join(re.escape(d) for d in digits)
    # Also allow common formatting chars around the whole number
    fmt = r"[\s()\-.+]*"
    return fmt + inner + fmt


@login_required
def index(request):
    extracted_text = None
    error = None
    filename = None
    extraction_done = False
    personal_info_form = PersonalInfoForm()
    removed_fields = []
    is_first_time = not Resume.objects.filter(user=request.user).exists()

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
                        removed_fields.append(field)
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
                        if field_name == "PHONE":
                            pattern = _make_flexible_phone_pattern(value)
                            if pattern is None:
                                continue
                        else:
                            pattern = re.escape(value)
                        extracted_text = re.sub(
                            pattern,
                            " ",
                            extracted_text,
                            flags=re.IGNORECASE,
                        )

                # Process extracted text with AI
                if extracted_text:
                    try:
                        client = OpenRouterClient(
                            command="""
                                Extract the data from this resume text and structure it into a 
                                JSON object, answer me with only the JSON object, here is the 
                                structure you need to follow:
                                {
                                    "resume": {
                                        "summary": "string",
                                        "work_experiences": [
                                        {
                                            "role": "string",
                                            "company": "string",
                                            "duration": "string",
                                            "description": "string"
                                        },
                                        ],
                                        "skills": [
                                            "string",
                                        ],
                                        "education": [
                                        {
                                            "degree": "string",
                                            "institution": "string",
                                            "graduation_year": "string"
                                        }
                                        ],
                                        "certificates": [
                                            "string",
                                        ],
                                        "languages": [
                                            "string",
                                        ],
                                        "links": [
                                            "string",
                                        ]
                                    }
                                }
                                """,
                            data=extracted_text,
                        )
                        resume_data = client.run()
                        extracted_text = resume_data

                        # Parse the JSON response and save to individual fields
                        if isinstance(resume_data, str):
                            parsed = json.loads(resume_data)
                        else:
                            parsed = resume_data
                        resume_fields = parsed.get("resume", parsed)

                        Resume.objects.update_or_create(
                            user=request.user,
                            defaults={
                                "summary": resume_fields.get("summary", ""),
                                "work_experiences": resume_fields.get(
                                    "work_experiences", ""
                                ),
                                "skills": resume_fields.get("skills", ""),
                                "education": resume_fields.get("education", ""),
                                "certificates": resume_fields.get("certificates", ""),
                                "languages": resume_fields.get("languages", ""),
                                "links": resume_fields.get("links", ""),
                            },
                        )

                        # Redirect to generate_cv after successful extraction
                        return redirect("generate_cv")
                    except Exception as e:
                        error = f"Processing failed. Please try again later."
                        print(f"Error during AI processing: {str(e)}")
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
        "resume/upload.html",
        {
            "form": form,
            "personal_info_form": personal_info_form,
            "extracted_text": extracted_text,
            "error": error,
            "filename": filename,
            "extraction_done": extraction_done,
            "removed_fields": removed_fields,
            "active_page": "extract",
            "is_first_time": is_first_time,
        },
    )
