from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse, Http404, HttpResponseRedirect
from recruiters.models import Recruiter, Organization, User

def indexView(request) :

    return HttpResponse('Welcome!')


def profileView(request) :

    return HttpResponse('Profile')


def postJobView(request) :
    
    return render(request, 'recruiters/postJob.html')

def createJobPostingView(request) :
    pass