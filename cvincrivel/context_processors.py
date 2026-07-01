from resume.models import Resume


def resume_context(request):
    """Add has_resume flag to template context for all authenticated users."""
    has_resume = False
    if request.user.is_authenticated:
        has_resume = Resume.objects.filter(user=request.user).exists()
    return {"has_resume": has_resume}
