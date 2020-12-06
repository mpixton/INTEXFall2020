from django.shortcuts import render 

# Create your views here.
from django.http import HttpResponse, Http404, HttpResponseRedirect

def jobListingsView(request) :

    return render (request, 'seekers/jobListings.html')

def profileView(request) :

    return HttpResponse('Profile')

def applicationView(request) :
    
    return HttpResponse('Apply Here')

def IndexPageView(request) :
    
    return render (request, 'seekers/index.html')

def loginPageView(request) :

    return render (request, 'seekers/login.html')