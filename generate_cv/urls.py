from django.urls import path

from . import views

urlpatterns = [
    path("", views.generate_cv, name="generate_cv"),
    path("download/<int:cv_id>/", views.download_cv, name="download_cv"),
]
