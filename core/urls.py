# URLS.py - App level 
from django.urls import path
from . import views
 
urlpatterns = [
    path('', views.home, name='home'),
    path('datalog/', views.datalog, name='datalog'),
]