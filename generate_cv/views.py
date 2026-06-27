from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .forms import GenerateCvForm


@login_required
def generate_cv(request):
    form = GenerateCvForm()
    return render(
        request,
        "generate_cv/generate_cv.html",
        {"form": form, "active_page": "generate"},
    )
