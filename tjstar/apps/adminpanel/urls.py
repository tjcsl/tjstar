from django.urls import path

from . import views

app_name = "adminpanel"

urlpatterns = [
    path('adminpanel/', views.adminpanel, name="index"),
]
