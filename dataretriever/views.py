from django.shortcuts import render

from .forms import ResumeUploadForm
from .extractors import extract_text_from_docx, extract_text_from_pdf


def index(request):
    extracted_text = None
    error = None
    filename = None
    extraction_done = False

    if request.method == "POST":
        form = ResumeUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES["file"]
            filename = uploaded_file.name
            file_bytes = uploaded_file.read()
            extraction_done = True

            try:
                if filename.lower().endswith(".docx"):
                    extracted_text = extract_text_from_docx(file_bytes)
                elif filename.lower().endswith(".pdf"):
                    extracted_text = extract_text_from_pdf(file_bytes)
                else:
                    error = "Unsupported file format."
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
            "extracted_text": extracted_text,
            "error": error,
            "filename": filename,
            "extraction_done": extraction_done,
        },
    )
