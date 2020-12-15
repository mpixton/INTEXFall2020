"""
View functions for the Seekers app.

View Functions:
    about: returns the about page
    IndexPageView: returns the home page
    SearchBar: allows a User to search listings
    searchJob: performs the search and renders results
    jobListingView: returns all jobs
    profileView: shows a logged in user's profile
    applicationView: allows a Job Seeker to apply to a listing
    CreateAccountView: returns a blank form for an Anonymous User to 
        register an account as either a Job Seeker or a Recruiter
    loginView: allows a User with an account to log in
    logoutView: logs out a logged in User
    AddSeekerSkillsView: allows a Seeker to add skills to their profile
    EditSeekerSkillsView: allows a Seeker to edit their skills 
    DeleteSeekerSkillsView: allows deletion of a Seeker's skill
    userApplicationsView: shows a Seeker the Listings they've 
        applied to
    recommenderDisplayView: returns results for a specific User using 
        the AZURE recommender service
    learnMoreView: takes the User to the learn more page
"""
# Python Imports
import operator
import json 
import urllib.request as lib
# Django Imports
from django.contrib import messages
from django.db import IntegrityError
from django.forms import ValidationError
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q, ObjectDoesNotExist
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User, Group
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
# App Imports
from seekers.forms import SeekerSignUpForm, RecruiterSignUpForm, AddSkillsForm, LoginForm, applyForm
from seekers.models import Listing, Seeker, SeekerSkill, Skill, Application, ListingSkill
from recruiters.models import Recruiter

#pylint:disable=no-member

ACCOUNT_TYPES = {
    'R': 'recruiter',
    'S': 'seeker',
}

def about(request) :
    """
    Sends the user to the about page.
    GET:
        About contains data about our project. (black unemployment, 
        why we are creating this)

        Args:
            None
    """
    return render(request, 'seekers/aboutUs.html')

def IndexPageView(request) :
    """
    Home page of the website.

    GET:
        Landing page for the website and central hub.

        Args: 
            None
    """
    return render (request, 'seekers/index.html')

def SearchBar(request, SearchString) :
    """
    Allows a User to search all Listings.

    GET: 
        Performs a fuzzy search on location, job title, and org based 
        on a given search string and returns the results.

        Args:
            SearchString: str, keyword the user wants to search
    """
    search = request.GET.get('search')
    post = Listing.objects.all().filter( Q (listing_job_title__icontains = search) | Q (location__icontains = search) | Q (posted_by__org__icontains=search))
    context = {
        "listings" : post
    }
    return render(request, 'seekers/jobListings.html', context)

# TODO refactor out? Potentially not being used      
def searchJob(request) :
    """
    Allows a user to view all jobs matching a query string.
    """
    search = request.POST.get('search')

    return redirect(reverse('Seekers:SearchResults', kwargs={'SearchString': search}))

def jobListingsView(request) :
    """
    Shows the user a list of all job listings. 

    GET:
        If Anonymous or Seeker, shows all Listings. If a recruiter, 
        shows only the listings associated with the logged in 
        Recruiter's org.

        Args: 
            None
    """
    # checks if the current user is anonymous or a recruiter
    # if anonymous, show all listings
    if request.user.is_anonymous :
        data = Listing.objects.all()
    # if recruiter, then only show listing where the poster belongs to the recruiter's org
    elif request.user.has_perm('recruiters.is_recruiter') :
        data = Listing.objects.filter(posted_by__org=Recruiter.objects.get(user=request.user).org)
    # display all listings
    else :
        data = Listing.objects.all()

    context = {
        "listings" : data
    }
    return render (request, 'seekers/jobListings.html', context)

@login_required(login_url='/login')
def profileView(request, Type, userID) :
    """
    Allows the user to view their own profile information

    GET: 
        Sends the User to their profile. For a Seeker, shows their 
        skills. For a Recruiters, shows their listings.

        Args:
            Type: str, the account type of the user (Seeker, Recruiter)
            userID: str or int, pk of the User account
    """
    # check the type of account
    # if seeker, find the account and render it
    if Type == 'seeker' :
        try :
            data = Seeker.objects.get(user=request.user)
            skills = SeekerSkill.objects.filter(seeker__user=request.user)
        except ObjectDoesNotExist :
            return HttpResponse("we couldn't find your account. do you have one?")
        context = {
            "profile" : data,    
            "skills" : skills,
        }
        return render(request, 'seekers/profile.html', context=context)
    # if recruiter, find the account and render it
    elif Type == 'recruiter' :
        try :
            data = Recruiter.objects.get(user=request.user)
            jobs = Listing.objects.filter(posted_by=data)
        except ObjectDoesNotExist :
            return HttpResponse("we couldn't find your account. do you have one?")

        context = {
            "profile" : data,    
            "jobs" : jobs,
        }
        return render(request, 'seekers/profile.html', context=context)

    else :
        return HttpResponse("Not found")

@login_required(login_url='/login')
@permission_required('seekers.is_seeker', raise_exception=True)
def applicationView(request, ListingID) :
    """
    Allows a Seeker to apply to a Listing.

    GET: 
        Serves a blank application for the Seeker to review.
        
        Args:
            ListingID: str or int, pk of the Listing to apply to
    POST:
        Creates the Application object, binding the Seeker to the 
        Listing.
    """
    # checks if method is GET or POST
    # if GET, render blank form
    if request.method == 'GET' :
        # create blank form with intitial data from the user
        form = applyForm(initial={'first_name': request.user.first_name, 'last_name': request.user.last_name, 'email': request.user.email})
        currentSeeker = Seeker.objects.get(user=request.user)
        # //TODO zip up the skill level names
        context={
            "skills": SeekerSkill.objects.filter(seeker=currentSeeker),
            "form": form,
            "listing": Listing.objects.get(pk=ListingID),
            'listingSkills': ListingSkill.objects.filter(listing=Listing.objects.get(pk=ListingID)),
        } 
        return render(request, 'seekers/apply.html', context)
    # if POST, create an application object 
    elif request.method == 'POST' :
        form = applyForm(request.POST)
        # check if form is valid
        if form.is_valid() :
            # error handling in case they've already applied
            try :
                # creates the application object and sets the seeker and listing
                seeker = Seeker.objects.get(user=request.user)
                listing = Listing.objects.get(pk=ListingID)
                Application.objects.create(seeker=seeker, listing=listing)
            except IntegrityError :
                context = {
                    'error': 'You have already applied to this job!',
                    'errorjob': Application.objects.get(seeker=seeker, listing=listing),
                    'listings': Listing.objects.all(),
                }
                # renders the page with the error message
                return render (request, 'seekers/jobListings.html', context)
            # if object is created successfully, render the job listings page with a success message
            context = {
                'success': Application.objects.get(seeker=seeker, listing=listing),
                'listings': Listing.objects.all(),
            }
            # renders the page with the success message
            return render (request, 'seekers/jobListings.html', context)
        # invalid form
        else:
            return HttpResponse('Form not valid to create and application')
    # invalid method
    else :
        return HttpResponse('invalid method called')

def CreateAccountView(request, AccountType) :
    """
    Allows an anonymous user to create an account.

    GET:
        Returns a blank sign up form based on the type of account to 
        create.

        Args:
            AccountType: str, type of account to create ('S', 'R')
    POST:
        Creates the request account type. Sends the User to their 
        profile page. 
    """
    # check the method used in the request
    # if GET, return a blank form depending on the type of user they want to create
    if  request.method == 'GET' :
        if AccountType == 'S' :
            form = SeekerSignUpForm()
        elif AccountType == 'R' :
            form = RecruiterSignUpForm()
        else :
            # TODO add a custom error message
            # maybe give a 403 error page?
            return HttpResponse('not a valid account type')
        # render the create account page
        return render(request, 'seekers/createAccount.html', {'form': form, 'AccType': AccountType})
    # if POST, create account
    elif request.method == 'POST':
        # if valid account type, puts the data in the proper form
        if AccountType == 'S' :
            # form = SeekerSignUpForm(request.POST, request.FILES['resume'])
            form = SeekerSignUpForm(request.POST)
        elif AccountType == 'R' :
            form = RecruiterSignUpForm(request.POST)
        else :
            return HttpResponse("didn't pass the account type check")
        # error handling in case something goes wrong
        # print(form)
        # print(request.user)
        # print(form.data)
        # print(request.POST)
        # print(form.is_valid())
        # print(form.data['phone'])
        # validates the form else 404
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            email = form.cleaned_data.get('email')
            try :
                # creates an account depending on the account type
                if AccountType == 'S' :
                    first_name = form.cleaned_data.get('first_name')
                    last_name = form.cleaned_data.get('last_name')
                    phone = form.cleaned_data.get('phone')
                    # resume = form.cleaned_data.get('resume')
                    # skill = form.cleaned_data.get('skill')
                    newUser = User.objects.create_user(username=username, password=password, email=email)
                    newUser.first_name = first_name
                    newUser.last_name = last_name
                    newUser.save()
                    # person = Seeker.objects.create(user=newUser, phone=phone, resume=resume, has_resume=True)
                    person = Seeker.objects.create(user=newUser, phone=phone, has_resume=False)
                    my_group = Group.objects.get(name='Seekers')
                    my_group.user_set.add(newUser)

                elif AccountType == 'R':
                    first_name = form.cleaned_data.get('first_name')
                    last_name = form.cleaned_data.get('last_name')
                    job_title = form.cleaned_data.get('employee_job_title')
                    org = form.cleaned_data.get('org_name')
                    newUser =  User.objects.create_user(username=username, password=password, email=email)
                    newUser.first_name = first_name
                    newUser.last_name = last_name
                    newUser.save()
                    person = Recruiter.objects.create(user=newUser, emp_job_title=job_title, org=org)
                    my_group = Group.objects.get(name='Recruiters')
                    my_group.user_set.add(newUser)
                # should be unreachable
                else :
                    return HttpResponse("didn't pass the account type creation check")
                # log the new user in
                authUser = authenticate(username=username, password=password)
                # require the returned user to have actually been created
                if authUser is not None :
                    login(request=request, user=authUser)
                    return redirect(reverse('Seekers:Profile', kwargs={'userID': person.pk, 'Type': ACCOUNT_TYPES.get(AccountType)}))
                else:
                    return HttpResponse('not a valid user')
            # if the user has already been created, but an error was raised, send them to the login page.
            except IntegrityError :
                context = {
                    'form': LoginForm(),
                    'messages': 'Your account has been created already. Please log in to continue.',
                }
                return render(request, 'seekers/login.html', context=context)
        # if form is not valid
        else :
            # repopulate the form with the data that they submitted
            if AccountType == 'S' :
                initialData = {
                    'email': request.POST['email'],
                    'username': request.POST['username'],
                    'first_name': request.POST['first_name'],
                    'last_name': request.POST['last_name'],
                    'phone': request.POST['phone'],
                }
            elif AccountType == 'R' :
                initialData = {
                    'email': request.POST['email'],
                    'username': request.POST['username'],
                    'first_name': request.POST['first_name'],
                    'last_name': request.POST['last_name'],
                    'employee_job_title': request.POST['employee_job_title'],
                    'org_name': request.POST['org_name'],
                }
            else :
                return HttpResponse('not a valid account type')
            # return HttpResponse('i am an invalid form on the create account view')
            form = RecruiterSignUpForm(initial=initialData)
            return render(request, 'seekers/createAccount.html', context={'form': form, 'AccType': AccountType,})
    else :
        return HttpResponse('I am not a valid method on the create account view')

def loginView(request) :
    """
    Logs in a User.

    GET:
        Sends a blank login form to allow a User to fill out their 
        credentials.

        Args:
            None
    POST:
        Logs the User in a sends them to the Index page.
    """
    # checks the method being used
    # if GET, sends a form to attempt a log in
    if request.method == 'GET' :
        form = LoginForm()
        return render(request = request, template_name = "seekers/login.html", context={"form":form})
    # if POST, attempts a login
    elif request.method == 'POST':
        form = LoginForm(request.POST)
        # checks if the form is valid
        if form.is_valid():
            # authenticates the user
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)

            # checks if the user exists in the system
            if user is not None:
                # logs in the user and redirects to the home page
                login(request, user)
                return redirect(reverse('Seekers:Index'))
            # user doesn't exist
            else :
                # returns an error message if no user found
                messages.error(request, "Invalid username or password.")
                form.add_error('password', 'Invalid username or password.')
                return render(request = request, template_name = "seekers/login.html", context={"form":form})
        # invalid form
        else :
            # returns error message if the form is not valid
            messages.error(request, "Invalid username or password.")
            form.add_error('password', 'Invalid username or password.')
            return render(request = request, template_name = "seekers/login.html", context={"form":form})
    # invalid method
    else:
        return HttpResponse('i am an invalid response on the loginView')

def logoutView(request) :
    """
    Logs a user out.

    GET:
        Logs the user out and sends them to the Home page.

        Args:
            None
    """
    logout(request)
    messages.info(request, "Logged out successfully!")
    return redirect("Seekers:Index")

@login_required(login_url='login/')
@permission_required('seekers.is_seeker', raise_exception=True)
def AddSeekerSkillsView(request) :
    """
    Allows a Seeker to add Skills to their profile.
    
    GET:
        Returns a blank form to allow a Seeker to add Skills.

        Args:
            None
    POST:
        Adds the selected Skill to the Seeker's profile by creating an 
        entry in the SeekerSkills table. Sends the Seeker to their 
        profile.
    """
    # check the method of the action
    # if GET, render a blank form to fill out
    if request.method == 'GET' :
        form = AddSkillsForm()
        return render(request = request, template_name = "seekers/addSkills.html", context={"form":form})
    # if POST, process the filled out form
    elif request.method == 'POST' :
        form = AddSkillsForm(request.POST)
        # checks if form is valid
        # if valid, create object
        if form.is_valid() :
            skill = form.cleaned_data.get('skill')
            level = form.cleaned_data.get('level')
            seeker = Seeker.objects.get(user=request.user)
            # check for validation errors.
            # if error raised, send them back to the form with the error message
            try :
                SeekerSkill.objects.create(seeker=seeker, skill=skill, level=level)
            except IntegrityError :
                form.add_error(field='skill', error='You already have this skill!')
                return render(request, 'seekers/addSkills.html', context={'form': form,})
            # render the profile if successful
            return redirect(reverse('Seekers:Profile', kwargs={'Type': 'seeker', 'userID': seeker.pk}))
        # invalid form
        else :
            return render(request, 'seekers/addSkills.html', context={'form': form,})
    # if invalid method, 
    else :
        return HttpResponse('i am an invalid method on the add skills view')

@login_required(login_url='login/')
@permission_required('seekers.is_seeker', raise_exception=True)
def EditSeekerSkillsView(request, SeekerSkillID) :
    """
    Allows a Seeker to edit their skills.
    
    GET:
        Renders a pre-filled form of the SeekerSkill to edit.

        Args:
            SeekerSkillID: str or int, pk of SeekerSkill to edit
    POST:
        Saves the edited SeekerSkill.
    """
    # checks the method used
    # if GET, renders blank form
    if request.method == 'GET' :
        editSkill = SeekerSkill.objects.get(pk=SeekerSkillID)
        intitialData = {
            'skill': editSkill.skill, 
            'level': editSkill.level,
        }
        context = {
            'form': AddSkillsForm(initial=intitialData),
        }
        return render(request, 'seekers/addSkills.html', context=context)
    # if POST, save the data and redirect to profile
    elif request.method == 'POST' :
        form = AddSkillsForm(request.POST)
        # check if form is valid
        # if valid, continue with update
        if form.is_valid() :
            editSkill = SeekerSkill.objects.get(pk=SeekerSkillID)
            editSkill.skill = form.cleaned_data.get('skill')
            editSkill.level = form.cleaned_data.get('level')
            # check for validation errors.
            # if error raised, send them back to the form with the error message
            try :
                editSkill.save()
            except ValidationError :
                # if error raised, send them back to the form with the error message
                return render(request, 'recruiters/addSkills.html', context={'form': form})

            # return to the profile page
            return redirect(reverse('Seekers:Profile', kwargs={'Type': 'seeker', 'userID': request.user.pk}))
        #if invalid, abort
        else :
            return HttpResponse('i am an invalid form on the edit seeker skills view')
    # invalid method
    else :
        return HttpResponse('i am a wrong method on the edit skills view')

@login_required(login_url='login/')
@permission_required('seekers.is_seeker', raise_exception=True)
def DeleteSeekerSkillsView(request, SeekerSkillID) :
    """
    Allows a Seeker to delete their skills.
    GET:
        Renders a pre-filled out form for the user to review prior to deleting.

        Args:
            SeekerSkillID: str or int, pk of the SeekerSkill to delete
    POST:
        Performs the delete on the SeekerSkill.
    """
    # checks the request method
    # if GET, renders the form with data populated
    if request.method == 'GET' :
        deleteSkill = SeekerSkill.objects.get(pk=SeekerSkillID)
        intialData = {
            'skill': deleteSkill.skill, 
            'level': deleteSkill.level,
        }
        context = {
            'form': AddSkillsForm(intialData),
        }
        # render the template
        return render(request, 'seekers/addSkills.html', context=context)
    # if POST, delete the listing and reroute to profile view
    elif request.method == 'POST' :
        deleteSkill = SeekerSkill.objects.get(pk=SeekerSkillID)
        deleteSkill.delete()
        return redirect(reverse('Seekers:Profile', kwargs={'Type': 'seeker', 'userID': request.user.pk,}))
    # else, display wrong method
    else :
        return HttpResponse('wrong method')

@login_required(login_url='login/')
@permission_required('seekers.is_seeker', raise_exception=True)
def userApplicationsView(request) :
    """
    Shows a Job Seeker the Listings they've applied to. 

    GET:
        Takes user to their applications.

        Args:
            None
    """
    seeker = Seeker.objects.get(user=request.user)
    applications = Application.objects.filter(seeker__user=request.user)
    context = {   
        "applications" : applications,
        "seeker" : seeker,
    }
    return render(request, 'seekers/applications.html', context=context)

def recommenderDisplayView(request) : 
    """
    Gets recommendations from the AZURE model.

    GET:
        Renders results for a predetermined user and job title.

        Args:
            None
    """
    data =  {
        "Inputs": {
            "input1": {
                "ColumnNames": ["user_id", "job_title"],
                "Values": [["72", "Marketing Consultant"]]
            }
        },
        "GlobalParameters": {}
    }

    body = str.encode(json.dumps(data))
    url = 'https://ussouthcentral.services.azureml.net/workspaces/f6ae6696799b45cbb93347b6e9d8ad6f/services/c88e62fc36a6497f846cab8bac6fb5b3/execute?api-version=2.0&details=true'
    api_key = 'CkEa9dvd5sBro9L5f04z1zqFpm1Drxp4vnr+Vhhd5EKbv9gBXNrX/aPZnFUSmUdjJKJLB0gbjQQtcSJugYhf7g==' # Replace this with the API key for the web service
    headers = {'Content-Type':'application/json', 'Authorization':('Bearer '+ api_key)}
    # generate request
    req = lib.Request(url, body, headers) 
    # Open/retrieve the request
    response = lib.urlopen(req)
    # Reads the request
    result = response.read()
    #cast result to json
    result = json.loads(result)

    prediction = result['Results']['output1']['value']['Values'][0]
    predictionData = {
        'Job_1' : str(f'1. {prediction[1]}'), 
        'Job_2' : str(f'2. {prediction[2]}'),
        'Job_3' : str(f'3. {prediction[3]}'),
        'Job_4' : str(f'4. {prediction[4]}'),
        'Job_5' : str(f'5. {prediction[5]}'),
        }
    
    return render(request, 'seekers/recommender.html', predictionData)

def learnMoreView (request) :
    """
    Sends a user to the LearnMore page.

    GET:
        Renders the LearnMore page.

        Args:
            None
    """
    return render(request, 'seekers/learnMore.html')