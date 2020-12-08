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
from seekers.models import Listing, Seeker, SeekerSkill, Skill
from django.contrib import messages
# from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from recruiters.models import Recruiter, Organization

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
        skills = SeekerSkill.objects.filter(seeker__user=request.user).values_list('skill__skill_name', 'level', named=True)
        if data is not None :
            context = {
                "seeker" : data,    
                "skills" : skills,
            }
            return render(request, 'seekers/profile.html', context=context)

    elif Type == 'recruiter' :
        data = Recruiter.objects.get(pk=userID)

        if data is not None :
            context = {
                "seeker" : data,
            }
            return render(request, 'seekers/profile.html', context=context)

    elif Type == 'organization' :
        data = Organization.objects.get(pk=userID)

        if data is not None :
            context = {
                "seeker" : data,
            }
            return render(request, 'seekers/profile.html', context=context)
    else :
        return HttpResponse("Not found")
        

@login_required
def applicationView(request) :
    
    form = applyForm(initial={'first_name':request.user.first_name, 'last_name':request.user.last_name, 'email':request.user.email})

    print(request.user)
    print(Seeker.objects.get(user=request.user.pk))
    print(Skill.objects.all())

    currentSeeker = Seeker.objects.get(pk=request.user)

    context={
        "skills": Skill.objects.filter(seekerskill__seeker=currentSeeker.pk),
        "form": form
    } 

    return render(request, 'seekers/addSkills.html', context)

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

            elif AccountType == 'O' :
                org_name = form.cleaned_data.get('org_name')
                size = form.cleaned_data.get('size')
                sector = form.cleaned_data.get('sector')
                newUser = User.objects.create_user(username=username, password=password, email=email)
                person = Organization.objects.create(user=newUser,  org_name=org_name, size=size, sector=sector)
                my_group = Group.objects.get(name='Organizations')
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
        elif AccountType == 'O' :
            form = OrganizationSignUpForm()
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