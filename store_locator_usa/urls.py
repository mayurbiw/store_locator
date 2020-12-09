from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("generate_report",views.generate_report,name="generate_report"),
    path("createreport/<brandname>",views.create_report,name="create_report"),
]