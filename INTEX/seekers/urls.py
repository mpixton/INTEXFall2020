from django.urls import path
import seekers.views as v

urlpatterns = [
    path("job_listings", v.jobListingsView, name="Job Listings"),
    path("profile/<str:userID>", v.profileView, name="Profile"),
    path("application", v.applicationView, name="Application"),
    path("", v.IndexPageView, name="Index"),
    path("login/", v.loginPageView, name="Login"),
]   