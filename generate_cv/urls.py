from django.urls import path

from . import views

urlpatterns = [
    path("", views.generate_cv, name="generate_cv"),
    path("download/<int:cv_id>/", views.download_cv, name="download_cv"),
    path("download/<int:cv_id>/docx/", views.download_cv_docx, name="download_cv_docx"),
    path("my-cvs/", views.cv_list, name="cv_list"),
    path("delete/<int:cv_id>/", views.delete_cv, name="delete_cv"),
    path("edit/<int:cv_id>/", views.edit_cv, name="edit_cv"),
]
