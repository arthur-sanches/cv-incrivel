from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import GenerateCvForm
from resume.models import Resume


@login_required
def generate_cv(request):
    # First-time user without resume data — send to setup page
    if not Resume.objects.filter(user=request.user).exists():
        return redirect("/profile_setup/")

    form = GenerateCvForm()
    return render(
        request,
        "generate_cv/generate_cv.html",
        {"form": form, "active_page": "generate"},
    )
