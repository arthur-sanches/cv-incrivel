import json
import re
from io import BytesIO

from html4docx import HtmlToDocx

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string

from weasyprint import HTML

from .forms import CvDownloadForm, EditGeneratedCVForm, GenerateCvForm
from .models import GeneratedCV
from resume.models import Resume
from ai_integration.services import OpenRouterClient


def _md_bold(text):
    """Convert **text** to <strong>text</strong>."""
    return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)


def _process_achievements(achievements):
    """Convert markdown bold in each achievement string."""
    return [_md_bold(a) for a in achievements]


def _process_skills(skills):
    """Convert markdown bold in each skill string."""
    return [_md_bold(s) for s in skills]


@login_required
def generate_cv(request):
    # First-time user without resume data — send to setup page
    if not Resume.objects.filter(user=request.user).exists():
        return redirect("/profile_setup/")

    result = None
    error = None
    generated_cv = None
    download_form = CvDownloadForm()

    if request.method == "POST":
        form = GenerateCvForm(request.POST)
        if form.is_valid():
            # Check if user has credits
            if request.user.credits <= 0:
                error = "You have no credits remaining. Please contact support to get more credits."
            else:
                job_description = form.cleaned_data["job_description"]
                resume = Resume.objects.get(user=request.user)

                # Build structured resume data
                resume_data = {
                    "summary": resume.summary,
                    "work_experiences": resume.work_experiences,
                    "skills": resume.skills,
                    "education": resume.education,
                    "certificates": resume.certificates,
                    "languages": resume.languages,
                    "links": resume.links,
                }

                payload = {
                    "job_description": job_description,
                    "resume": resume_data,
                }

                try:
                    client = OpenRouterClient(
                        command="""You are an elite Executive Resume Writer and ATS Optimization Specialist tasked with 
                            transforming raw career data into high-impact, tailored resumes. Your outputs must be 
                            strictly data-driven, utilizing the Google X-Y-Z formula ("Accomplished [X], as 
                            measured by [Y], by doing [Z]") to emphasize quantifiable achievements over mere 
                            responsibilities. Write exclusively in the implicit third-person (never using "I," "me," 
                            or "my"), meticulously eliminating corporate fluff, buzzwords, and subjective soft 
                            skills in favor of concrete domain expertise and hard metrics. Ensure every concise 
                            bullet point begins with a powerful, non-repeating action verb and strictly uses the 
                            past tense for previous roles. Optimize the document for Applicant Tracking Systems by 
                            naturally embedding target keywords and using standard structural headers (Professional 
                            Summary, Core Competencies, Experience, Education), outputting the final result in clean 
                            Markdown with key metrics and achievements from the summary and job experiences bolded for 
                            maximum visual scannability. Do not invent any information or achievements, only use the data 
                            provided.
                            Skills should be grouped into categories and the categories should be bold.

                            Use the "resume" information provided to generate a tailored CV for the "job_description". 
                            The output should be in the same language as the "job_description" and in JSON format, 
                            strictly adhering to the following structure:

                            {
                                "headings": {
                                    "professional_summary": "string",
                                    "professional_experience": "string",
                                    "education": "string",
                                    "skills": "string",
                                    "certificates": "string",
                                    "languages": "string"
                                },
                                "resume": {
                                    "summary": "string",
                                    "experience": [
                                        {
                                            "job_title": "string",
                                            "company": "string",
                                            "duration": "string",
                                            "achievements": ["string"]
                                        }
                                    ],
                                    "skills": ["string"],
                                    "education": [
                                        {
                                            "degree": "string",
                                            "institution": "string",
                                            "duration": "string (e.g. \"2017-2020\")"
                                        }
                                    ],
                                    "certificates": ["string"],
                                    "languages": ["string"],
                                    "links": ["string"]
                                }
                            }
                            """,
                        data=json.dumps(payload, indent=2),
                        model="xiaomi/mimo-v2.5-pro",
                        provider={
                            "allow_fallbacks": True,
                            "order": [
                                "atlas-cloud/fp8",
                                "novita",
                            ],
                        },
                    )
                    result = client.run()

                    # Strip markdown code fences if present (e.g. ```json ... ```)
                    cleaned = result.strip()
                    if cleaned.startswith("```"):
                        # Remove opening fence (```json, ```, etc.) and closing fence
                        cleaned = (
                            cleaned.split("\n", 1)[-1] if "\n" in cleaned else cleaned
                        )
                        cleaned = (
                            cleaned.rsplit("```", 1)[0] if "```" in cleaned else cleaned
                        )
                        cleaned = cleaned.strip()

                    # Parse the JSON response and save to database
                    try:
                        parsed = json.loads(cleaned)
                        resume_data = parsed.get("resume", {})
                        headings_data = parsed.get("headings", {})

                        generated_cv = GeneratedCV.objects.create(
                            user=request.user,
                            name=f"CV - {job_description[:50]}",
                            professional_summary=resume_data.get("summary", ""),
                            work_experiences=json.dumps(
                                resume_data.get("experience", []), indent=2
                            ),
                            skills=json.dumps(resume_data.get("skills", []), indent=2),
                            education=json.dumps(
                                resume_data.get("education", []), indent=2
                            ),
                            certificates=json.dumps(
                                resume_data.get("certificates", []), indent=2
                            ),
                            languages=json.dumps(
                                resume_data.get("languages", []), indent=2
                            ),
                            links=json.dumps(resume_data.get("links", []), indent=2),
                            headings=json.dumps(headings_data, indent=2),
                        )

                        # Deduct one credit after successful generation
                        request.user.credits -= 1
                        request.user.save(update_fields=["credits"])

                        download_form = CvDownloadForm(
                            initial={"name": generated_cv.name}
                        )
                        result = "CV generated successfully! Enter a file name and click Download to save your PDF."
                    except (json.JSONDecodeError, KeyError, TypeError) as e:
                        print(f"Error saving generated CV: {str(e)}")
                except Exception as e:
                    error = "Generation failed. Please try again later."
                    print(f"Error during CV generation: {str(e)}")
    else:
        form = GenerateCvForm()

    return render(
        request,
        "generate_cv/generate_cv.html",
        {
            "form": form,
            "result": result,
            "error": error,
            "generated_cv": generated_cv,
            "download_form": download_form,
            "active_page": "generate",
        },
    )


@login_required
def download_cv(request, cv_id):
    generated_cv = get_object_or_404(GeneratedCV, pk=cv_id, user=request.user)

    if request.method == "POST":
        form = CvDownloadForm(request.POST)
        if form.is_valid():
            generated_cv.name = form.cleaned_data["name"]
            generated_cv.save(update_fields=["name"])

    # Parse JSON fields back into lists
    try:
        experience_list = (
            json.loads(generated_cv.work_experiences)
            if generated_cv.work_experiences
            else []
        )
    except json.JSONDecodeError:
        experience_list = []

    try:
        skills_list = json.loads(generated_cv.skills) if generated_cv.skills else []
    except json.JSONDecodeError:
        skills_list = []

    try:
        education_list = (
            json.loads(generated_cv.education) if generated_cv.education else []
        )
    except json.JSONDecodeError:
        education_list = []

    try:
        certificates_list = (
            json.loads(generated_cv.certificates) if generated_cv.certificates else []
        )
    except json.JSONDecodeError:
        certificates_list = []

    try:
        languages_list = (
            json.loads(generated_cv.languages) if generated_cv.languages else []
        )
    except json.JSONDecodeError:
        languages_list = []

    try:
        links_list = json.loads(generated_cv.links) if generated_cv.links else []
    except json.JSONDecodeError:
        links_list = []

    try:
        headings = json.loads(generated_cv.headings) if generated_cv.headings else {}
    except json.JSONDecodeError:
        headings = {}

    # Get user's resume for contact info
    resume = get_object_or_404(Resume, user=request.user)

    # Process markdown bold to HTML bold
    for exp in experience_list:
        exp["achievements"] = _process_achievements(exp.get("achievements", []))
    skills_list = _process_skills(skills_list)
    professional_summary = _md_bold(generated_cv.professional_summary)

    context = {
        "name": resume.name or "",
        "contact_email": resume.contact_email or "",
        "phone": resume.phone or "",
        "address": resume.address or "",
        "professional_summary": professional_summary,
        "experience_list": experience_list,
        "skills_list": skills_list,
        "education_list": education_list,
        "certificates_list": certificates_list,
        "languages_list": languages_list,
        "links_list": links_list,
        "headings": headings
        or {
            "professional_summary": "Professional Summary",
            "professional_experience": "Professional Experience",
            "education": "Education",
            "skills": "Technical Skills",
            "certificates": "Certificates",
            "languages": "Languages",
        },
    }

    html_string = render_to_string("cv_templates/1.html", context)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{generated_cv.name}.pdf"'

    HTML(string=html_string).write_pdf(response)

    return response


@login_required
def download_cv_docx(request, cv_id):
    generated_cv = get_object_or_404(GeneratedCV, pk=cv_id, user=request.user)

    if request.method == "POST":
        form = CvDownloadForm(request.POST)
        if form.is_valid():
            generated_cv.name = form.cleaned_data["name"]
            generated_cv.save(update_fields=["name"])

    # Parse JSON fields back into lists
    try:
        experience_list = (
            json.loads(generated_cv.work_experiences)
            if generated_cv.work_experiences
            else []
        )
    except json.JSONDecodeError:
        experience_list = []

    try:
        skills_list = json.loads(generated_cv.skills) if generated_cv.skills else []
    except json.JSONDecodeError:
        skills_list = []

    try:
        education_list = (
            json.loads(generated_cv.education) if generated_cv.education else []
        )
    except json.JSONDecodeError:
        education_list = []

    try:
        certificates_list = (
            json.loads(generated_cv.certificates) if generated_cv.certificates else []
        )
    except json.JSONDecodeError:
        certificates_list = []

    try:
        languages_list = (
            json.loads(generated_cv.languages) if generated_cv.languages else []
        )
    except json.JSONDecodeError:
        languages_list = []

    try:
        links_list = json.loads(generated_cv.links) if generated_cv.links else []
    except json.JSONDecodeError:
        links_list = []

    try:
        headings = json.loads(generated_cv.headings) if generated_cv.headings else {}
    except json.JSONDecodeError:
        headings = {}

    # Get user's resume for contact info
    resume = get_object_or_404(Resume, user=request.user)

    # Process markdown bold to HTML bold
    for exp in experience_list:
        exp["achievements"] = _process_achievements(exp.get("achievements", []))
    skills_list = _process_skills(skills_list)
    professional_summary = _md_bold(generated_cv.professional_summary)

    context = {
        "name": resume.name or "",
        "contact_email": resume.contact_email or "",
        "phone": resume.phone or "",
        "address": resume.address or "",
        "professional_summary": professional_summary,
        "experience_list": experience_list,
        "skills_list": skills_list,
        "education_list": education_list,
        "certificates_list": certificates_list,
        "languages_list": languages_list,
        "links_list": links_list,
        "headings": headings
        or {
            "professional_summary": "Professional Summary",
            "professional_experience": "Professional Experience",
            "education": "Education",
            "skills": "Technical Skills",
            "certificates": "Certificates",
            "languages": "Languages",
        },
    }

    html_string = render_to_string("cv_templates/1.html", context)

    parser = HtmlToDocx()
    docx = parser.parse_html_string(html_string)

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
    response["Content-Disposition"] = f'attachment; filename="{generated_cv.name}.docx"'

    buffer = BytesIO()
    docx.save(buffer)
    buffer.seek(0)
    response.write(buffer.read())

    return response


@login_required
def cv_list(request):
    cvs = GeneratedCV.objects.filter(user=request.user)
    return render(
        request,
        "generate_cv/cv_list.html",
        {
            "cvs": cvs,
            "active_page": "my_cvs",
        },
    )


@login_required
def delete_cv(request, cv_id):
    generated_cv = get_object_or_404(GeneratedCV, pk=cv_id, user=request.user)

    if request.method == "POST":
        generated_cv.delete()

    return redirect("cv_list")


@login_required
def edit_cv(request, cv_id):
    generated_cv = get_object_or_404(GeneratedCV, pk=cv_id, user=request.user)

    if request.method == "POST":
        form = EditGeneratedCVForm(request.POST)
        if form.is_valid():
            generated_cv.name = form.cleaned_data["name"]
            generated_cv.professional_summary = form.cleaned_data[
                "professional_summary"
            ]
            generated_cv.work_experiences = form.cleaned_data["work_experiences"]
            generated_cv.skills = form.cleaned_data["skills"]
            generated_cv.education = form.cleaned_data["education"]
            generated_cv.certificates = form.cleaned_data["certificates"]
            generated_cv.languages = form.cleaned_data["languages"]
            generated_cv.links = form.cleaned_data["links"]
            generated_cv.headings = form.cleaned_data["headings"]
            generated_cv.save()
            return redirect("cv_list")
    else:
        initial = {
            "name": generated_cv.name,
            "professional_summary": generated_cv.professional_summary,
            "work_experiences": _pretty_json(generated_cv.work_experiences),
            "skills": _pretty_json(generated_cv.skills),
            "education": _pretty_json(generated_cv.education),
            "certificates": _pretty_json(generated_cv.certificates),
            "languages": _pretty_json(generated_cv.languages),
            "links": _pretty_json(generated_cv.links),
            "headings": _pretty_json(generated_cv.headings),
        }
        form = EditGeneratedCVForm(initial=initial)

    return render(
        request,
        "generate_cv/edit_cv.html",
        {
            "form": form,
            "generated_cv": generated_cv,
            "active_page": "my_cvs",
        },
    )


def _pretty_json(value):
    """Try to pretty-print a JSON string; return original on failure."""
    if not value or not value.strip():
        return ""
    try:
        parsed = json.loads(value)
        return json.dumps(parsed, indent=2)
    except (json.JSONDecodeError, TypeError):
        return value
