from django.shortcuts import render, redirect

# Create your views here.
#pylint:disable=no-member
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.forms import ValidationError
from django.urls import reverse
from seekers.forms import SeekerSignUpFrom, RecruiterSignUpForm, OrganizationSignUpForm, AddSkillsForm, LoginForm, applyForm
from seekers.models import Listing, Seeker, SeekerSkill, Skill, Application
from recruiters.models import Recruiter
from django.contrib import messages
# from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from recruiters.models import Recruiter
from django.db.models import Q
import operator
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.views.generic import ListView
from django.db import IntegrityError



ACCOUNT_TYPES = {
    'R': 'recruiter',
    'S': 'seeker',
    'O': 'organization',
}

def about(request) :
    """
    Sends the user to the about page. \n
    Takes no parameters. \n
    About contains data about our project. (black unemployment, why we are creating this)
    """
    
    return render(request, 'seekers/aboutUs.html')

def IndexPageView(request) :
    """
    Home page of the website. \n
    no parameters.
    """
    
    return render (request, 'seekers/index.html')


def SearchBar(request, SearchString) :
    search = request.GET.get('search')
    post = Listing.objects.all().filter( Q (listing_job_title__icontains = search) | Q (location__icontains = search) | Q (posted_by__org__icontains=search))
    context = {
        "listings" : post
    }
    return render(request, 'seekers/jobListings.html', context)

       
def searchJob(request) :
    """
    Allows a user to view all jobs matching a query string.
    """
    search = request.POST.get('search')

    return redirect(reverse('Seekers:SearchResults', kwargs={'SearchString': search}))
    

def jobListingsView(request) :
    """
    Shows the user a list of all job listings.
    """
    data = Listing.objects.all()

    context = {
        "listings" : data
    }

    return render (request, 'seekers/jobListings.html', context)

def SearchResultsView(request, SearchString) :
    """
    Displays the results of the search. \n
    SearchString -> a string to match against job_title, location, org_name
    """
    jobTitle = request.GET['listingJobTitle']
    data = Listing.objects.filter(job_title = jobTitle)
    if data.count() > 0:
        context = {
            "listings" : data
        }
        return render(request, 'seekers/jobListings.html', context)
    else:
        organization = request.GET['organization']
        data = Listing.objects.filter(org = organization)
        if data.count() > 0 :
            context = {
            "listings" : data
            }
            return render(request, 'seekers/jobListings.html', context)
        else :
            location = request.GET['city'] 
            data = Listing.objects.filter(job_loc = location)
            if data.count() > 0 :
                context = {
                "listings" : data
                }
                return render(request, 'seekers/jobListings.html', context)
            else :
                return HttpResponse("Not found")

@login_required
def profileView(request, Type, userID) :
    """
    Allows the user to view their own profile information. \n
    userID -> str, the pk of the User
    """
    if Type == 'seeker' :
        data = Seeker.objects.get(user=request.user)
        skills = SeekerSkill.objects.filter(seeker__user=request.user)
        
        if data is not None :
            context = {
                "profile" : data,    
                "skills" : skills,
            }
            return render(request, 'seekers/profile.html', context=context)

    elif Type == 'recruiter' :
        data = Recruiter.objects.get(user=request.user)
        jobs = Listing.objects.filter(posted_by=data)

        if data is not None :
            context = {
                "profile" : data,    
                "jobs" : jobs,
            }
            return render(request, 'seekers/profile.html', context=context)

    else :
        return HttpResponse("Not found")
    

@login_required
def applicationView(request, ListingID) :
    """
    Handles serving a blank application for Seeker review (GET method) or creates an application object (POST method) associated with the Seeker. \n
    Takes no parameters.
    """
    # checks if method is GET or POST
    # if GET, render blank form
    if request.method == 'GET' :
        # create blank form with intitial data from the user
        form = applyForm(initial={'first_name':request.user.first_name, 'last_name':request.user.last_name, 'email':request.user.email})
        # set current Seeker user
        currentSeeker = Seeker.objects.get(user=request.user)
        # set context variable
        # //TODO zip up the skill level names
        context={
            "skills": SeekerSkill.objects.filter(seeker=currentSeeker),
            "form": form,
            "listing": Listing.objects.get(pk=ListingID),
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
                # sets the error context
                context = {
                    'error': 'You have already applied to this job!',
                    'errorjob': Application.objects.get(seeker=seeker, listing=listing),
                    'listings': Listing.objects.all(),
                }
                # renders the page with the error message
                return render (request, 'seekers/jobListings.html', context)
            # if object is created successfully, render the job listings page
            return redirect(reverse('Seekers:JobListings'))
        
        else:
            return HttpResponse('Form not valid to create and application')
    
    # else
    else :
        return HttpResponse('invalid method called')


def CreateAccountView(request, AccountType) :
    """
    Allows an anonymous user to create an account. \n
    Account Types: S -> Seeker, O -> Organization, R -> Recruiter \n
    If passed a parameter that doesn't match, returns a 404 error.
    """
    # checks if POST or GET, if not, 404
    if request.method == 'POST':
        # check if valid account type else 4040
        # if valid account type, puts the data in the proper form
        if AccountType == 'S' :
            form = SeekerSignUpFrom(request.POST)
        elif AccountType == 'R' :
            form = RecruiterSignUpForm(request.POST)
        else :
            return HttpResponse('didn\'t pass the account type check')
        
        # validates the form else 404
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            email = form.cleaned_data.get('email')

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
                person = Seeker.objects.create(user=newUser, phone=phone, has_resume=False)
                my_group = Group.objects.get(name='Seekers')
                my_group.user_set.add(newUser)

            elif AccountType == 'R':
                print(form)
                print(form.cleaned_data.get('first_name'))
                print(form.cleaned_data.get('last_name'))
                print(form.cleaned_data.get('username'))
                print(form.cleaned_data.get('password'))
                print(form.cleaned_data.get('employee_job_title'))
                print(form.cleaned_data.get('org_name'))
                first_name = form.cleaned_data.get('first_name')
                last_name = form.cleaned_data.get('last_name')
                job_title = form.cleaned_data.get('employee_job_title')
                org = form.cleaned_data.get('org_name')
                newUser =  User.objects.create_user(username=username, password=password, email=email)
                newUser.first_name = first_name
                newUser.last_name = last_name
                newUser.save()
                print(newUser)
                person = Recruiter.objects.create(user=newUser, emp_job_title=job_title, org=org)
                print(person)
                my_group = Group.objects.get(name='Recruiters')
                print(my_group)
                my_group.user_set.add(newUser)
            
            # should be unreachable
            else :
                return HttpResponse('didn\'t pass the account type creation check')

            authUser = authenticate(username=username, password=password)
            
            # require the returned user to have actually been created
            # log in the user, else 404
            # 404 should be unreachable
            if authUser is not None :
                login(request=request, user=authUser)
                return redirect(reverse('Seekers:Profile', kwargs={'userID': person.pk, 'Type': ACCOUNT_TYPES.get(AccountType)}))
            else:
                return HttpResponse('not a valid user')

    # if get, return a blank form depending on the type of user they want to create
    # if not a valid type, 404
    elif request.method == 'GET' :
        if AccountType == 'S' :
            form = SeekerSignUpFrom()
        elif AccountType == 'R' :
            form = RecruiterSignUpForm()
        else :
            return HttpResponse('not a valid account type')

        return render(request, 'seekers/createAccount.html', {'form': form, 'AccType': AccountType})
    else :
        return HttpResponse('Not a valid method')

def loginView(request) :
    """
    Logs a user in by authenticating them against a list of known users. Sends them to the Index page. \n
    Takes no GET parameters. All data passed through POST.
    """
    # checks if trying to log in (via POST) else sends a login form to attempt a login
    if request.method == 'POST':
        # fills out the login form with data from the form definition
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
                messages.info(request, f"You are now logged in as {username}")
                return redirect(reverse('Seekers:Index'))

            else :
                # returns an error message if no user found
                messages.error(request, "Invalid username or password.")
                return render(request = request, template_name = "seekers/login.html", context={"form":form})

        else :
            # returns error message if the form is not valid
            messages.error(request, "Invalid username or password.")
            return render(request = request, template_name = "seekers/login.html", context={"form":form})

    # if get, sends a form to attempt a log in
    elif request.method == 'GET' :
        
        form = LoginForm()
        return render(request = request, template_name = "seekers/login.html", context={"form":form})
    
    # if any other method, 404
    else:
        return Http404

def logoutView(request) :
    """
    Logs a user out
    """
    logout(request)
    messages.info(request, "Logged out successfully!")
    return redirect("Seekers:Index")

def addSkillsView(request) :
    if request.method == 'POST' :
        form = AddSkillsForm(request.POST)
        if form.is_valid() :
            skill = form.cleaned_data.get('skill')
            level = form.cleaned_data.get('level')
            seeker = Seeker.objects.get(user=request.user)
            SeekerSkill.objects.create(seeker=seeker, skill=skill, level=level)
            return redirect(reverse('Seekers:Profile', kwargs={'Type': 'seeker', 'userID': seeker.pk}))
        else :
            return Http404()
    elif request.method == 'GET' :

        form = AddSkillsForm()
        
        return render(request = request,
                template_name = "seekers/addSkills.html",
                context={"form":form})
    else :
        return Http404()


def userApplicationsView(request) :
    user = Seeker.objects.get(user=request.user)
    applications = Application.objects.filter(seeker__user=request.user)
    context = {   
        "applications" : applications,
        "user" : user,
    }
    return render(request, 'seekers/applications.html', context=context)
