from django.urls import path

from . import views

app_name = "lookup"

urlpatterns = [
    path('', views.home, name="index"),
    path('presentations/', views.presentations, name="presentations"),
]