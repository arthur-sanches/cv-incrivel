import json

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import GenerateCvForm
from .models import GeneratedCV
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
                        Markdown with key metrics bolded for maximum visual scannability. Do not invent any 
                        information or achievements, only use the data provided.

                        Use the "resume" information provided to generate a tailored CV for the "job_description". 
                        The output should be in the same language as the "job_description" and in JSON format, 
                        strictly adhering to the following structure:

                        {
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
                                        "graduation_year": "string"
                                    }
                                ],
                                "certificates": ["string"],
                                "languages": ["string"],
                                "links": ["string"]
                            }
                        }
                        """,
                    data=json.dumps(payload, indent=2),
                    model="deepseek/deepseek-v4-flash",
                )
                result = client.run()

                # Parse the JSON response and save to database
                try:
                    parsed = json.loads(result)
                    resume_data = parsed.get("resume", {})

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
                    )
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
            "active_page": "generate",
        },
    )
