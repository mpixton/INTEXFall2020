"""
View functions for the Recruiters app.

Functions:
    applicantsView: displays all applicants to a Listing.
    AddListingView: allows a Recruiter to add a Listing.
    EditListingView: allows a Recruiter to edit a Listing.
    DeleteListingView: allows a Recruiter to delete a Listing.
    AddListingSkillView: allows a Recruiter to add a Listing Skill.
    EditListingSkillView: allows a Recruiter to edit a Listing Skill.
    DeleteListingSkillView: allows a Recruiter to delete a Listing Skill.
"""
# Python Imports

# Django Imports
from django.db import IntegrityError
from django.forms import ValidationError
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required, permission_required
# App Imports
from recruiters.forms import PostJobForm, AddListingSkillForm
from recruiters.models import Recruiter, User
from seekers.models import Listing, Skill, ListingSkill, ContractLength, ContractType

# pylint:disable=no-member

@login_required()
@permission_required('recruiters.is_recruiter', raise_exception=True)
def applicantsView(request) :
    """
    Displays all Job Seekers that have applied to a Listing.

    GET:
        Shows a Recruiter the applicant's to their Listings.

        Args:
            None
    """
    recruiter = Recruiter.objects.get(user=request.user)
    jobs = Listing.objects.filter(posted_by=recruiter)

    context = {   
        "recruiter" : recruiter,
        "jobs" : jobs,
    }
    return render(request, 'recruiters/applicants.html', context=context)

@login_required()
@permission_required('recruiters.is_recruiter', raise_exception=True)
def AddListingView(request) :
    """
    Allows a Recruiter to create a new job listing 

    GET:
        Return a blank form for the Recruiter to fill out.

        Args:
            None
    POST:
        Create the Listing from the form the Recruiter filled out and 
        redirects them to their profile to verify it went through.
    """
    # check the request method
    # if GET, render blank form
    if request.method == 'GET' :
        context = {
            'form': PostJobForm(),
        }
        return render(request, 'recruiters/postJob.html', context=context)
    # if POST, create the listing and send the recruiter to the profile page
    elif request.method == 'POST' :
        form = PostJobForm(request.POST)
        # check if form is valid
        # if valid, add the listing
        if form.is_valid() :
            job_title = form.cleaned_data.get('job_title')
            job_description = form.cleaned_data.get('job_description')
            location = form.cleaned_data.get('location')
            contract_length = form.cleaned_data.get('contract_length')
            contract_type = form.cleaned_data.get('contract_type')
            poster = Recruiter.objects.get(user=request.user)
            salary_upper = form.cleaned_data.get('salary_upper')
            salary_lower = form.cleaned_data.get('salary_lower')
            reloc = form.cleaned_data.get('reloc')
            
            Listing.objects.create(
                listing_job_title=job_title, 
                job_description=job_description, 
                location=location, 
                contract_length=contract_length, 
                contract_type=contract_type, 
                posted_by=poster, 
                salary_lower=salary_lower, 
                salary_upper=salary_upper, 
                relocation_assistance=reloc
                )
            # send the Recruiter to their profile
            return redirect(reverse('Seekers:Profile', kwargs={'Type': 'recruiter', 'userID': request.user.pk}))
        # if invalid form, render the Post Job page with the form's errors
        else :
            return render(request, 'recruiters/postJob.html', context={'form': form})
    # invalid method 
    else :
        return HttpResponse('i am an invalid method on the post job view')
    
@login_required()
@permission_required('recruiters.is_recruiter', raise_exception=True)
def EditListingView(request, ListingID):
    """
    Allows a Recruiter to edit a listing previously posted.

    GET: 
        Returns the Listing data in a form for the Recruiter to edit.
        
        Args:
            ListingID: pk of the Listing to be edited
    POST:
        Saves the changes made on the form to the model and redirects the 
        Recruiter to their profile to verify it went through.
    """
    # checks the request method
    # if GET, return the listing for review
    if request.method == 'GET' : 
        listing = Listing.objects.get(pk=ListingID)
        # creates the intital data to populate the form with
        intialData = {
            'job_title': listing.listing_job_title,
            'job_description': listing.job_description,
            'location': listing.location,
            'contract_length': listing.contract_length,
            'contract_type': listing.contract_type,
            'salary_upper': listing.salary_upper,
            'salary_lower': listing.salary_lower,
            'reloc': listing.relocation_assistance,
        }
        context = {
            'form': PostJobForm(intialData),
            'ListingID': listing.pk,
            'ListingSkills': ListingSkill.objects.filter(listing=listing),
        }
        # renders the form
        return render(request, 'recruiters/postJob.html', context=context)
    # if POST, save the data and redirect to profile
    elif request.method == 'POST' :
        form = PostJobForm(request.POST) 
        # check if form is valid
        # if valid, proceed with update
        if form.is_valid() :
            updateListing = Listing.objects.get(pk=ListingID)

            updateListing.job_title = form.cleaned_data.get('job_title')
            updateListing.job_description = form.cleaned_data.get('job_description')
            updateListing.location = form.cleaned_data.get('location')
            updateListing.contract_length = form.cleaned_data.get('contract_length')
            updateListing.contract_type = form.cleaned_data.get('contract_type')
            updateListing.salary_lower = form.cleaned_data.get('salary_lower')
            updateListing.salary_upper = form.cleaned_data.get('salary_upper')
            updateListing.relocation_assistance = form.cleaned_data.get('reloc')
            updateListing.save()
            # redirect to the profile page
            return redirect(reverse('Seekers:Profile', kwargs={'Type': 'recruiter', 'userID': request.user.pk}))
        # if invalid, display the edit Page with the form errors
        else :
            return render(request, 'recruiters/postJob.html', context={'form': form,})
    # invalid method
    else :
        return HttpResponse('i am an invalid method on the edit listing view')

@login_required()
@permission_required('recruiters.is_recruiter', raise_exception=True)
def DeleteListingView(request, ListingID) :
    """
    Allows a Recruiter to delete a listing previously posted.
    
    GET:
        Returns a form with data to review prior to deletion.

        Args:
            ListingID: pk of the Listing object to delete
    POST:
        Deletes the selected Listing and redirects the Recruiter to their 
        profile to verify the deletion went through.
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
            'salary_upper': listing.salary_upper,
            'salary_lower': listing.salary_lower,
            'reloc': listing.relocation_assistance,
        }

        context = {
            'form': PostJobForm(intialData),
            'ListingSkills': ListingSkill.objects.filter(listing=listing),
            'Listing': listing.pk,
        }
        # render the template
        return render(request, 'recruiters/postJob.html', context=context)
    # if POST, delete the listing and reroute to profile view
    elif request.method == 'POST' :
        listingToDelete = Listing.objects.get(pk=ListingID)

        listingToDelete.delete()            
        # redirects to the profile to confirm delete
        return redirect(reverse('Seekers:Profile', kwargs={'Type': 'recruiter', 'userID': request.user.pk}))
    # invalid method
    else :
        return HttpResponse('I am a wrong method on the delete listing view')

@login_required()
@permission_required('recruiters.is_recruiter', raise_exception=True)
def AddListingSkill(request, ListingID) :
    """
    Adds a Skill to a Listing.

    GET: 
        Returns a blank form to allow a Recruiter to add a Skill to the Listing.

        Args:
            ListingID: pk of the Listing object to add a Listing Skill to
    POST:
        Adds the Skill to the Listing via the ListingSkill table and 
        redirects the Recruiter to their profile to verify it went 
        through.
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
        form = AddListingSkillForm(request.POST) 
        # check form for validation errors
        # if error raised, send them back to the form with the error message
        try :
            form.is_valid()
        except ValidationError :
            return render(request, 'recruiters/addSkill.html', context={'form': form,})
        # check if form is valid
        # if valid, procedd with creating the skill
        if form.is_valid() :
            skill = form.cleaned_data.get('skill')
            level = form.cleaned_data.get('level')
            is_required = form.cleaned_data.get('is_required')
            # check if the skill-listing pairing already exists.
            try :
                ListingSkill.objects.create(skill=skill, level=level, listing=Listing.objects.get(pk=ListingID), is_required=is_required)
            except IntegrityError :
                form.add_error(field='skill', error='This skill is already associated with this listing!')
                return render(request, 'recruiters/addSkill.html', context={'form': form, 'Listing': ListingID,})
            # redirect the user to the Listing to see the skills
            return redirect(reverse('Recruiters:EditListing', kwargs={'ListingID': ListingID}))
        # if not valid, return form with errors
        else :
            return render(request, 'recruiters/addSkill.html', context={'form': form, 'Listing': ListingID})
    # invalid method
    else :
        return HttpResponse('I am a wrong method on the add listing skills')

@login_required()
@permission_required('recruiters.is_recruiter', raise_exception=True)
def EditListingSkillView(request, ListingSkillID) :
    """
    Allows editing of the ListingSkills associated with a Listing.
    
    GET:
        Returns a bound form with the ListingSkills data to edit.

        Args:
            ListingSkillID: pk of the ListingSkill object to be edited
    POST:
        Saves the changes to the ListingSkill and redirects to the 
        Recruiter's profile to verify it went through.
    """ 
    # checks the method used to access the action
    # if GET, return bound form
    if request.method == 'GET' :
        updateLS = ListingSkill.objects.get(pk=ListingSkillID)
        # populate initial data for the form
        initialData = {
            'skill': updateLS.skill,
            'level': updateLS.level,
            'is_required': updateLS.is_required,
        }

        context ={
            'form': AddListingSkillForm(initialData),
            'Listing': updateLS.listing,
            'OtherSkills': ListingSkill.objects.filter(listing=updateLS.listing).exclude(pk=ListingSkillID),
        }
        # render the template
        return render(request, 'recruiters/addSkill.html', context=context)
    # if POST, save changes 
    elif request.method == 'POST' :
        form = AddListingSkillForm(request.POST)
        # check for validation errors.
        # if error raised, send them back to the form with the error message
        try :
            form.is_valid()
        except ValidationError :
            return render(request, 'recruiters/addSkill.html', context={'form': form,})
        # checks if new data is valid
        # if valid, proceed
        if form.is_valid() :
            updateLS = ListingSkill.objects.get(pk=ListingSkillID)

            updateLS.skill = form.cleaned_data.get('skill')
            updateLS.level = form.cleaned_data.get('level')
            updateLS.is_required = form.cleaned_data.get('is_required')
            updateLS.save()
            # redirects back to the edit listing page
            return redirect(reverse('Recruiters:EditListing', kwargs={'ListingID':updateLS.listing.pk}))
        else :
            return render(request, 'recruiters/addSkill.html', context={'form': form, 'Listing': updateLS.pk})
    # invalid method
    else :
        return HttpResponse('I am a wrong method on the edit listing skills call')

@login_required()
@permission_required('recruiters.is_recruiter', raise_exception=True)
def DeleteListingSkillView(request, ListingSkillID) :
    """
    Allows a Recruiter to delete a ListingSkill.

    GET: 
        Returns a bound form for review prior to deletion.
    
        Args:
            ListingSkillID: pk of the ListingSkill object to be deleted
    POST:
        Deletes the ListingSkill instance and returns the Recruiter to the 
        editListing page.
    """
    # check the method used
    # if GET, return bound form with data for review
    if request.method == 'GET' :
        lstoDelete = ListingSkill.objects.get(pk=ListingSkillID)
        # populate initial data for the form
        initialData = {
            'skill': lstoDelete.skill,
            'level': lstoDelete.level,
            'is_required': lstoDelete.is_required,
        }

        context ={
            'form': AddListingSkillForm(initialData),
            'Listing': lstoDelete.listing,
            'OtherSkills': ListingSkill.objects.filter(listing=lstoDelete.listing).exclude(pk=ListingSkillID),
        }
        # render the template
        return render(request, 'recruiters/addSkill.html', context=context)
    # if POST, delete the object
    elif request.method == 'POST' :
        lsToDelete = ListingSkill.objects.get(pk=ListingSkillID)
        # gets the listing to return to before deleting the instance
        listingID = lsToDelete.listing

        lsToDelete.delete()
        # redirects to the Listing page that the Listing Skill we just deleted was associated with
        return  redirect(reverse('Recruiters:EditListing', kwargs={'ListingID':listingID.pk}))
    # else invalid method
    else :
        return HttpResponse('I am a wrong method error on the delete listing skills call')