from django.shortcuts import render, redirect

# Create your views here.
# pylint:disable=no-member
from django.http import HttpResponse, Http404, HttpResponseRedirect
from recruiters.models import Recruiter, User
from seekers.models import Listing, Skill, ListingSkill, ContractLength, ContractType
from recruiters.forms import PostJobForm, AddListingSkillForm
from django.urls import reverse

def indexView(request) :
    """
    Index view of the recruiters app. \n
    Takes no GET parameters. \n
    """

    return HttpResponse('Welcome!')


def applicantsView(request) :
    """
    Shows a Recruiter Job Seekers that have applied to Listings posted by the logged in Recruiter. \n
    """

    recruiter = Recruiter.objects.get(user=request.user)
    jobs = Listing.objects.filter(posted_by=recruiter)

    context = {   
        "recruiter" : recruiter,
        "jobs" : jobs,
    }
    return render(request, 'recruiters/applicants.html', context=context)


def createJobPostingView(request) :
    """
    Allows a Recruiter to create a new job listing. \n
    If GET method used, return a blank form to create the listing \n
    If POST method used, create the listing using the form \n
    """
    # check the request method
    # if GET, render blank form
    if request.method == 'GET' :
        # instantiate the blank form
        context = {
            'form': PostJobForm(),
        }
        return render(request, 'recruiters/postJob.html', context=context)
    # if POST, create the listing and send the recruiter to the profile page
    elif request.method == 'POST' :
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
    # unreachable
    return redirect(reverse('Seekers:Profile', kwargs={'Type': 'recruiter', 'userID': request.user.pk}))


def EditListingView(request, ListingID):
    """
    Allows a Recruiter to edit a listing previously posted \n
    GET parameters: ListingID-> pk of the Listing to be edited \n
    If GET method used, returns the current data to for review \n
    If POST method used, updates the object \n
    """
    # checks the request method
    # if GET, return the listing for review
    if request.method == 'GET' : 
        # pulls object from DB
        listing = Listing.objects.get(pk=ListingID)
        # creates the intital data to populate the form with
        intialData = {
            'job_title': listing.listing_job_title,
            'job_description': listing.job_description,
            'location': listing.location,
            'contract_length': listing.contract_length,
            'contract_type': listing.contract_type,
        }
        # creates the context
        context = {
            'form': PostJobForm(intialData),
            'ListingID': listing.pk,
            'ListingSkills': ListingSkill.objects.filter(listing=listing),
        }
        # renders the form
        return render(request, 'recruiters/postJob.html', context=context)
    # if POST, save the data and redirect to profile
    elif request.method == 'POST' :
        # pulls the object to update
        updateListing = Listing.objects.get(pk=ListingID)
        updateListing.job_title = request.POST.get('job_title')
        updateListing.job_description = request.POST.get('job_description')
        updateListing.location = request.POST.get('location')
        updateListing.contract_length = ContractLength.objects.get(pk=request.POST.get('contract_length'))
        updateListing.contract_type = ContractType.objects.get(pk=request.POST.get('contract_type'))
        updateListing.save()
        # redirect to the profile page
        return redirect(reverse('Seekers:Profile', kwargs={'Type': 'recruiter', 'userID': request.user.pk}))
    # else, display wrong method
    else :
        return HttpResponse('wrong method')


def DeleteListingView(request, ListingID) :
    """
    Allows a Recruiter to delete a listing previously posted \n
    GET parameters: ListingID-> pk of the Listing object to delete \n
    If GET method used, returns the form with the data to preview before deletion \n
    If POST method used, deletes the listing \n
    """
    # checks the request method
    # if GET, renders the form with data populated
    if request.method == 'GET' :
        # gets the listing
        listing = Listing.objects.get(pk=ListingID)
        # populates the initial data dict
        intialData = {
            'job_title': listing.listing_job_title,
            'job_description': listing.job_description,
            'location': listing.location,
            'contract_length': listing.contract_length,
            'contract_type': listing.contract_type,
        }

        context = {
            'form': PostJobForm(intialData),
            'ListingSkills': ListingSkill.objects.filter(listing=listing),
        }
        # render the template
        return render(request, 'recruiters/postJob.html', context=context)
    # if POST, delete the listing and reroute to profile view
    elif request.method == 'POST' :
        # gets the listing to delete
        listingToDelete = Listing.objects.get(pk=ListingID)
        # deletes the listing
        listingToDelete.delete()
        # redirects to the profile to confirm delete
        return redirect(reverse('Seekers:Profile', kwargs={'Type': 'recruiter', 'userID': request.user.pk,}))
    # else, display wrong method
    else :
        return HttpResponse('wrong method')


def AddListingSkill(request, ListingID) :
    """
    Adds a Skill to a Listing. \n
    GET Parameters: ListingID-> pk of the Listing object to add a Listing Skill to \n
    If GET method used, returns a blank form to allow a Recruiter to add a Skill to the Listing \n
    If POST method used, adds the Skill to the Listing via the ListingSKill table \n
    """
    # check the method
    # if GET, return a blank form
    if request.method == 'GET' :
        context = {
            'form': AddListingSkillForm(),
            'Listing': Listing.objects.get(pk=ListingID), 
        }   
        return render(request, 'recruiters/addSkill.html', context=context)
    # if POST, create a new ListingSkill object
    elif request.method == 'POST' :
        # put all data in the form
        form = AddListingSkillForm(request.POST) 
        # check if form is valid
        if form.is_valid() :
            skill = form.cleaned_data.get('skill')
            level = form.cleaned_data.get('level')
            is_required = form.cleaned_data.get('is_required')
            ListingSkill.objects.create(skill=skill, level=level, listing=Listing.objects.get(pk=ListingID), is_required=is_required)
            # redirect the user to the Listing to see the skills
            return redirect(reverse('Recruiters:EditListing', kwargs={'ListingID': ListingID}))
        # if not valid, tell the user
        else :
            return HttpResponse('I am an invalid form in the ListingSkills section')
    else :
        return HttpResponse('I am a wrong method on the add listing skills')


def EditListingSkillView(request, ListingSkillID) :
    """
    Allows a Recruiter to edit the ListingSkills associated with their listing \n
    GET parameters: ListingSkillID-> pk of the ListingSkill object to be edited \n
    If GET method used, returns a bound form with the ListingSkills data to edit \n
    If POST method used, saves the changes to the skill \n
    """ 
    # checks the method used to access the action
    # if GET, return bound form
    if request.method == 'GET' :
        # get the ListingSkill instance
        updateLS = ListingSkill.objects.get(pk=ListingSkillID)
        # populate initial data for the form
        initialData = {
            'skill': updateLS.skill,
            'level': updateLS.level,
            'is_required': updateLS.is_required,
        }
        # set context
        context ={
            'form': AddListingSkillForm(initialData),
            'Listing': updateLS.listing,
            'OtherSkills': ListingSkill.objects.filter(listing=updateLS.listing).exclude(pk=ListingSkillID),
        }
        # render the template
        return render(request, 'recruiters/addSkill.html', context=context)
    # if POST, save changes to the form
    elif request.method == 'POST' :
        form = AddListingSkillForm(request.POST)
        # checks if new data is valid
        if form.is_valid() :
            # gets the ListingSkill instance
            updateLS = ListingSkill.objects.get(pk=ListingSkillID)
            # updates the ListingSkill instance
            updateLS.skill = form.cleaned_data.get('skill')
            updateLS.level = form.cleaned_data.get('level')
            updateLS.is_required = form.cleaned_data.get('is_required')
            updateLS.save()
            # redirects back to the edit listing page
            return redirect(reverse('Recruiters:EditListing', kwargs={'ListingID':updateLS.listing.pk}))
        else :
            return HttpResponse('i am an invalid form on the edit listing skills call')
    else :
        return HttpResponse('I am a wrong method on the edit listing skills call')


def DeleteListingSkillView(request, ListingSkillID) :
    """
    Allows a user to delete the Skill associated with the Listing. \n
    GET parameters: ListingSkillID-> pk of the ListingSkill object to be deleted \n
    If GET method used, returns a bound form for review prior to deletion \n
    If POST method used, deletes the ListingSkill instance and returns the Recruiter to the editListing page. \n
    """
    # check the method used
    # if GET, return bound form with data for review
    if request.method == 'GET' :
        # get the ListingSkill instance
        updateLS = ListingSkill.objects.get(pk=ListingSkillID)
        # populate initial data for the form
        initialData = {
            'skill': updateLS.skill,
            'level': updateLS.level,
            'is_required': updateLS.is_required,
        }
        # set context
        context ={
            'form': AddListingSkillForm(initialData),
            'Listing': updateLS.listing,
            'OtherSkills': ListingSkill.objects.filter(listing=updateLS.listing).exclude(pk=ListingSkillID),
        }
        # render the template
        return render(request, 'recruiters/addSkill.html', context=context)
    elif request.method == 'POST' :
        # get the instance to delete
        lsToDelete = ListingSkill.objects.get(pk=ListingSkillID)
        # gets the listing to return to before deleting the instance
        listingID = lsToDelete.listing
        # deletes the listing skill
        lsToDelete.delete()
        # redirects to the Listing page that the Listing Skill we just deleted was associated with
        return  redirect(reverse('Recruiters:EditListing', kwargs={'ListingID':listingID.pk}))
    # else invalid method, return an error string
    else :
        return HttpResponse('I am a wrong method error on the delete listing skills call')