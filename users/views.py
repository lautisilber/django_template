from django.shortcuts import render
from django.http import HttpResponse, HttpRequest

def create(request: HttpRequest):
    return HttpResponse('<h1>Create user</h1>')