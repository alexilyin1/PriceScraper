from django.urls import path, include
from . import views

app_name = 'django_select2'

urlpatterns = [
    path('', views.home),
    path('/second', views.second)
]