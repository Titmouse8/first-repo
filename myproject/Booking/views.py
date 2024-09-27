from django.shortcuts import render
from templates import *
# Create your views here.

def index(request):
    return render(request, 'index.html', {})