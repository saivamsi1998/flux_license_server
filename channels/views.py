from django.shortcuts import render
from django.http import HttpResponse,HttpRequest


# Create your views here.
def index(request: HttpRequest) -> HttpResponse:
    return HttpResponse("Hello you're at channels index")