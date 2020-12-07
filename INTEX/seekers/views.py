from django.shortcuts import render, redirect

# Create your views here.
#pylint:disable=no-member
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
# from django.contrib.auth.models import User
from django.forms import ValidationError
from django.urls import reverse
from seekers.forms import SeekerSignUpFrom, RecruiterSignUpForm, OrganizationSignUpForm, addSkills
from seekers.models import Listing, Seeker, SeekerSkills
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from recruiters.models import Recruiter, Organization

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

def searchJob(request) :
    """
    Allows a user to view all jobs matching a query string.
    """
    jobTitle = request.GET['listingJobTitle']
    data = Listing.objects.filter(job_title = jobTitle)
    if data.count() > 0:
        context = {
            "related_jobs" : data
        }
        return render(request, 'seekers/displayJobs.html', context)
    else:
        organization = request.GET['organization']
        data = Listing.objects.filter(org = organization)
        if data.count() > 0 :
            context = {
            "related_jobs" : data
            }
            return render(request, 'seekers/displayJobs.html', context)
        else :
            location = request.GET['city'] 
            data = Listing.objects.filter(job_loc = location)
            if data.count() > 0 :
                context = {
                "related_jobs" : data
                }
                return render(request, 'seekers/displayJobs.html', context)
            else :
                return HttpResponse("Not found")

def jobListingsView(request) :
    """
    Shows the user a list of all job listings.
    """
    data = Listing.objects.all()

    context = {
        "listings" : data
    }
    return render (request, 'seekers/jobListings.html', context)

@login_required
def profileView(request, userID) :
    """
    Allows the user to view their own profile information. \n
    userID -> str, the pk of the User
    """
    user = request.user
    data = Seeker.objects.filter(user)

    return HttpResponse('Profile')

@login_required
def applicationView(request) :
    
    return HttpResponse('Apply Here')

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
        elif AccountType == 'O' :
            form = OrganizationSignUpForm(request.POST)
        else :
            return Http404
        
        # validates the form else 404
        if form.is_valid():
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password')
            email = form.cleaned_data.get('email')

            # creates an account depending on the account type
            if AccountType == 'S' :
                first_name = form.cleaned_data.get('first_name')
                last_name = form.cleaned_data.get('last_name')
                phone = form.cleaned_data.get('phone')
                # resume = form.cleaned_data.get('resume')
                # skill = form.cleaned_data.get('skill')
                authUser = Seeker.objects.create(username=username, password=raw_password, first_name=first_name, last_name = last_name, email=email, phone=phone, has_resume=False, )

            elif AccountType == 'R':
                first_name = form.cleaned_data.get('first_name')
                last_name = form.cleaned_data.get('last_name')
                phone = form.cleaned_data.get('phone')
                job_title = form.cleaned_data.get('emp_job_title')
                authUser =  Recruiter.objects.create(username=username, password=raw_password, first_name=first_name, last_name = last_name, email=email, phone=phone, emp_job_title=job_title)

            elif AccountType == 'O' :
                org_name = form.cleaned_data.get('org_name')
                size = form.cleaned_data.get('size')
                sector = form.cleaned_data.get('sector')
                authUser = Organization.objects.create(username=username, password=raw_password, email=email, org_name=org_name, size=size, sector=sector)
            
            # should be unreachable
            else :
                return Http404()

            authUser = authenticate(username=username, password=raw_password)
            
            # require the returned user to have actually been created
            # log in the user, else 404
            # 404 should be unreachable
            if authUser is not None :
                login(request=request, user=authUser)
                return redirect(reverse('Seekers:Index'))
            else:
                return Http404()

    # if get, return a blank form depending on the type of user they want to create
    # if not a valid type, 404
    elif request.method == 'GET' :
        if AccountType == 'S' :
            form = SeekerSignUpFrom()
        elif AccountType == 'R' :
            form = RecruiterSignUpForm()
        elif AccountType == 'O' :
            form = OrganizationSignUpForm()
        else :
            return Http404()

        return render(request, 'seekers/createAccount.html', {'form': form, 'AccType': AccountType})
    else :
        return Http404()

def loginView(request) :
    """
    Logs a user in by authenticating them against a list of known users. Sends them to the Index page. \n
    Takes no GET parameters. All data passed through POST.
    """
    # checks if trying to log in (via POST) else sends a login form to attempt a login
    if request.method == 'POST':
        form = AuthenticationForm(request=request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}")
                return redirect(reverse('Seekers:Index'))
            else :
                messages.error(request, "Invalid username or password.")
        else :
            messages.error(request, "Invalid username or password.")
    form = AuthenticationForm()
    return render(request = request,
                    template_name = "seekers/login.html",
                    context={"form":form})


def logoutView(request) :
    logout(request)
    messages.info(request, "Logged out successfully!")
    return redirect("Seekers:Index")

def addSkillsView(request) :
    if request.method == 'POST' :
        form = addSkills(request.POST)
        if form.is_valid() :
            skill = form.cleaned_data.get('skill')
            level = form.cleaned_data.get('level')
            SeekerSkills.objects.create(user=request.user, skill=skill, level=level)
            return redirect(reverse('Seekers:Profile'))
        else :
            return Http404()
    elif(request.method == 'GET') :
        form = addSkills()
        return render(request = request,
                template_name = "seekers/addSkills.html",
                context={"form":form})
    else :
        return Http404()            