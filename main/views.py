from django.shortcuts import render
from django.http import HttpResponse, HttpRequest

def home(request: HttpRequest):
    return HttpResponse('<h1>Home</h1>')


def get(request: HttpRequest):
    return HttpResponse(str(request.GET.dict()))