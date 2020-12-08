from django.shortcuts import render, redirect

# Create your views here.
# pylint:disable=no-member
from django.http import HttpResponse, Http404, HttpResponseRedirect
from recruiters.models import Recruiter, User
from seekers.models import Listing, Skill
from recruiters.forms import PostJobForm
from django.urls import reverse

def indexView(request) :

    return HttpResponse('Welcome!')


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
        job_description = form.cleaned_data.get('job_description')
        location = form.cleaned_data.get('location')
        contract_length = form.cleaned_data.get('contract_length')
        contract_type = form.cleaned_data.get('contract_type')
        poster = Recruiter.objects.get(user=request.user)

        Listing.objects.create(listing_job_title=job_title, job_description=job_description, location=location, contract_length=contract_length, contract_type=contract_type, posted_by=poster)
    else :
        return HttpResponse('Not a valid user')

    return redirect(reverse('Seekers:Profile', kwargs={'Type': 'recruiter', 'userID': request.user.pk}))

def applicantsView(request) :
    user = Recruiter.objects.get(user=request.user)
    applicants = ""
    # applications = Application.objects.filter(seeker__user=request.user)
    context = {
        "applicants" : applicants,    
        "user" : user,
    }
    return render(request, 'recruiters/applicants.html', context=context)