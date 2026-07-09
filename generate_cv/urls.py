from django.urls import path

from . import views

urlpatterns = [
    path("", views.generate_cv, name="generate_cv"),
    path("download/<int:cv_id>/", views.download_cv, name="download_cv"),
    path("my-cvs/", views.cv_list, name="cv_list"),
    path("delete/<int:cv_id>/", views.delete_cv, name="delete_cv"),
]
