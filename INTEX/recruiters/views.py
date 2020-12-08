from django.shortcuts import render, redirect

# Create your views here.
# pylint:disable=no-member
from django.http import HttpResponse, Http404, HttpResponseRedirect
from recruiters.models import Recruiter, Organization, User
from seekers.models import Listing, Skill
from recruiters.forms import PostJobForm
from django.urls import reverse

def indexView(request) :

    return HttpResponse('Welcome!')


def profileView(request) :

    return HttpResponse('Profile')


def postJobView(request) :

    form = PostJobForm(request.POST)

    return render(request, 'recruiters/postJob.html', {'form': form})

def createJobPostingView(request) :
    
    if request.method == 'POST' :
        form = PostJobForm(request.POST)
    else :
        return HttpResponse('Error')

    if form.is_valid() :
        job_title = form.cleaned_data.get('job_title')
        organization = form.cleaned_data.get('organization')
        job_description = form.cleaned_data.get('job_description')
        location = form.cleaned_data.get('location')
        contract_length = form.cleaned_data.get('contract_length')
        contract_type = form.cleaned_data.get('contract_type')

        Listing.objects.create(listing_job_title=job_title, organization=organization, job_description=job_description, location=location, contract_length=contract_length, contract_type=contract_type)
    else :
        return HttpResponse('Not a valid user')

    return redirect(reverse('Recruiters:PostJob'))