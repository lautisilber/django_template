from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='main-home'),
    path('get', views.get, name='main-get'),
]