import json

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import GenerateCvForm
from resume.models import Resume
from ai_integration.services import OpenRouterClient


@login_required
def generate_cv(request):
    # First-time user without resume data — send to setup page
    if not Resume.objects.filter(user=request.user).exists():
        return redirect("/profile_setup/")

    result = None
    error = None

    if request.method == "POST":
        form = GenerateCvForm(request.POST)
        if form.is_valid():
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
                    command="Change this later",
                    data=json.dumps(payload, indent=2),
                )
                result = client.run()
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
            "active_page": "generate",
        },
    )
