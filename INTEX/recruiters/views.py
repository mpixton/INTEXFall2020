from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse, Http404, HttpResponseRedirect

def indexView(request) :

    return HttpResponse('Welcome!')

def applicantListingsView(request) :

    return HttpResponse('Applicants Listings')

def addListingsView(request) :

    return HttpResponse('Add Listings')

def profileView(request) :

    return HttpResponse('Profile')