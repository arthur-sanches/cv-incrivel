from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from resume.models import Resume

from .forms import ProfileForm


@login_required
def profile_view(request):
    if not Resume.objects.filter(user=request.user).exists():
        return redirect("/profile_setup/")

    resume, _ = Resume.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = ProfileForm(request.POST, instance=resume)
        if form.is_valid():
            form.save()
            return render(
                request,
                "profile/profile.html",
                {
                    "form": ProfileForm(instance=resume),
                    "active_page": "profile",
                    "saved": True,
                },
            )
    else:
        form = ProfileForm(instance=resume)

    return render(
        request,
        "profile/profile.html",
        {
            "form": form,
            "active_page": "profile",
        },
    )
