from django.urls import path
import seekers.views as v

app_name = 'Seekers'
urlpatterns = [
    path("job_listings", v.jobListingsView, name="Job Listings"),
    path("profile/<str:userID>", v.profileView, name="Profile"),
    path("application", v.applicationView, name="Application"),
    path("", v.IndexPageView, name="Index"),
]   