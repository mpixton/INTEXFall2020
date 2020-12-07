from django.urls import path
import seekers.views as v 

app_name = 'Seekers'
urlpatterns = [
    path("job_listings", v.jobListingsView, name="JobListings"),
    path("profile/<str:userID>", v.profileView, name="Profile"),
    path("application", v.applicationView, name="Application"),
    path("search", v.searchJob, name="Search"),
    path("create_account/<str:AccountType>", v.CreateAccountView, name="CreateAccount"),
    path("login", v.loginView, name="Login"),
    path("logout", v.logoutView,name="Logout"),
    path("about", v.about, name ="About"),
    path("add_skills", v.addSkillsView, name="AddSkills"),
    path("", v.IndexPageView, name="Index"),
]   