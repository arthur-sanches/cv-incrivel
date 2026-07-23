from resume.models import Resume


def resume_context(request):
    """Add has_resume flag and user credits to template context for all authenticated users."""
    has_resume = False
    user_credits = 0
    if request.user.is_authenticated:
        has_resume = Resume.objects.filter(user=request.user).exists()
        user_credits = request.user.credits
    return {"has_resume": has_resume, "user_credits": user_credits}
