from django.shortcuts import render, redirect

#To do:
#- allow a seeker to edit their skills
#- when a seeker tries to add the same skill it throughs an http error 


# Create your views here.
#pylint:disable=no-member
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User, Group
from django.forms import ValidationError
from django.urls import reverse
from seekers.forms import SeekerSignUpForm, RecruiterSignUpForm, AddSkillsForm, LoginForm, applyForm
from seekers.models import Listing, Seeker, SeekerSkill, Skill, Application, ListingSkill
from recruiters.models import Recruiter
from django.contrib import messages
# from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from recruiters.models import Recruiter
from django.db.models import Q, ObjectDoesNotExist
import operator
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.views.generic import ListView
from django.db import IntegrityError
import urllib.request as lib
import json 



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
    Shows the user a list of all job listings \n
    Only called on GET, takes no parameters \n
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
    Allows the user to view their own profile information \n
    GET parameters: Type-> type of account to be viewed, userID-> pk of the user to view the profile of \n
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
        try :
            data = Recruiter.objects.get(user=request.user)
            jobs = Listing.objects.filter(posted_by=data)
        except ObjectDoesNotExist :
            pass

        if data is not None :
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
    Handles serving a blank application for Seeker review (GET method) or creates an application object (POST method) associated with the Seeker \n
    GET parameters: ListingID-> pk of the Listing object to apply for \n
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
                # sets the error context
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
            # renders the page with the error message
            return render (request, 'seekers/jobListings.html', context)
        
        else:
            return HttpResponse('Form not valid to create and application')
    
    # else
    else :
        return HttpResponse('invalid method called')


def CreateAccountView(request, AccountType) :
    """
    Allows an anonymous user to create an account. \n
    GET parameters: AccountType-> type of account to create \n
    Account Types: S -> Seeker, O -> Organization, R -> Recruiter \n
    If passed a parameter that doesn't match, returns a 404 error. \n
    """
    # check the method used in the request
    # if get, return a blank form depending on the type of user they want to create
    if  request.method == 'GET' :
        if AccountType == 'S' :
            form = SeekerSignUpForm()
        elif AccountType == 'R' :
            form = RecruiterSignUpForm()
        else :
            return HttpResponse('not a valid account type')
        # render the create account page
        return render(request, 'seekers/createAccount.html', {'form': form, 'AccType': AccountType})
    # checks if POST or GET, if not, 404
    elif request.method == 'POST':
        # check if valid account type else 4040
        # if valid account type, puts the data in the proper form
        if AccountType == 'S' :
            # form = SeekerSignUpForm(request.POST, request.FILES['resume'])
            form = SeekerSignUpForm(request.POST)
        elif AccountType == 'R' :
            form = RecruiterSignUpForm(request.POST)
        else :
            return HttpResponse('didn\'t pass the account type check')
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
                form = SeekerSignUpForm(initial=initialData)
            # repopulate the form with the data that they submitted
            elif AccountType == 'R' :
                initialData = {
                    'email': request.POST['email'],
                    'username': request.POST['username'],
                    'first_name': request.POST['first_name'],
                    'last_name': request.POST['last_name'],
                    'employee_job_title': request.POST['employee_job_title'],
                    'org_name': request.POST['org_name'],
                }
                form = RecruiterSignUpForm(initial=initialData)
            else :
                return HttpResponse('not a valid account type')
            
            # return HttpResponse('i am an invalid form on the create account view')
            return render(request, 'seekers/createAccount.html', context={'form': form, 'AccType': AccountType,})
    else :
        return HttpResponse('I am not a valid method on the create account view')

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


@login_required(login_url='login/')
@permission_required('seekers.is_seeker', raise_exception=True)
def AddSeekerSkillsView(request) :
    """
    If called by GET, returns a blank form for a job seeker to fill out. If called via a POST, adds a skills to job seeker. \n
    Take no GET parameters. \n
    If GET, returns blank form. 
    If POST, adds the selected skill to the Seeker, \n
    """
    # check the method of the action
    # if GET, render a blank form to fill out
    if request.method == 'GET' :
        # instantiate blank form
        form = AddSkillsForm()
        # return the blank 
        return render(request = request, template_name = "seekers/addSkills.html", context={"form":form})
    # if POST, process the filled out form
    elif request.method == 'POST' :
        # fill out the form
        form = AddSkillsForm(request.POST)
        # if form is valid, post the form 
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
        # form is not valid
        else :
            return render(request, 'seekers/addSkills.html', context={'form': form,})
    # if invalid method, 
    else :
        return HttpResponse('i am an invalid method on the add skills view')


@login_required(login_url='login/')
@permission_required('seekers.is_seeker', raise_exception=True)
def EditSeekerSkillsView(request, SeekerSkillID) :
    """
    Allows a Seeker to edit their skills. \n
    GET parameters: SeekerSkillID -> pk of the SeekerSkill to edit \n
    If GET method used, renders the Skill to edit \n
    If POST method used, saves the changes \n
    """
    # checks the method used
    # if GET, renders blank form
    if request.method == 'GET' :
        # get the skill to edit
        editSkill = SeekerSkill.objects.get(pk=SeekerSkillID)
        # populate the inital data dict
        intitialData = {
            'skill': editSkill.skill, 
            'level': editSkill.level,
        }
        # sets the context
        context = {
            'form': AddSkillsForm(initial=intitialData),
        }
        # render the add skills page
        return render(request, 'seekers/addSkills.html', context=context)
    # if POST, save the data and redirect to profile
    elif request.method == 'POST' :
        # puts the data in the form to validate it
        form = AddSkillsForm(request.POST)
        # check if form is valid
        # if valid, continue with update
        if form.is_valid() :
            #gets the skill to edit
            editSkill = SeekerSkill.objects.get(pk=SeekerSkillID)
            editSkill.skill = form.cleaned_data.get('skill')
            editSkill.level = form.cleaned_data.get('level')
            # check for validation errors.
            # if error raised, send them back to the form with the error message
            try :
                editSkill.save()
            except ValidationError :
                # if error raised, send them back to the form with the error message
                return render(request, 'recruiters/addSkills.html', context={'form': form,})
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
    Allows a Seeker to delete their skills. \n
    GET parameters: SeekerSkillID -> pk of the SeekerSkill to delete \n
    If GET, renders the Skill to delete for review\n
    If POST, deletes the Skill \n
    """
    # checks the request method
    # if GET, renders the form with data populated
    if request.method == 'GET' :
        # gets the SeekerSkill
        deleteSkill = SeekerSkill.objects.get(pk=SeekerSkillID)
        # populates the initial data dict
        intialData = {
            'skill': deleteSkill.skill, 
            'level': deleteSkill.level,
        }
        # sets the context variable
        context = {
            'form': AddSkillsForm(intialData),
        }
        # render the template
        return render(request, 'seekers/addSkills.html', context=context)
    # if POST, delete the listing and reroute to profile view
    elif request.method == 'POST' :
        # gets the SeekerSkill to delete
        deleteSkill = SeekerSkill.objects.get(pk=SeekerSkillID)
        # deletes the SeekerSkill
        deleteSkill.delete()
        # redirects to the profile to confirm delete
        return redirect(reverse('Seekers:Profile', kwargs={'Type': 'seeker', 'userID': request.user.pk,}))
    # else, display wrong method
    else :
        return HttpResponse('wrong method')


@login_required(login_url='login/')
@permission_required('seekers.is_seeker', raise_exception=True)
def userApplicationsView(request) :
    seeker = Seeker.objects.get(user=request.user)
    applications = Application.objects.filter(seeker__user=request.user)
    context = {   
        "applications" : applications,
        "seeker" : seeker,
    }
    return render(request, 'seekers/applications.html', context=context)


def recommenderDisplayView(request) : 
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



    return render(request, 'seekers/learnMore.html')