from django.urls import path
import recruiters.views as v

app_name = 'Recruiters'
urlpatterns = [
    # path("applicant_listings", v.applicantListingsView, name="Applicant Listings"),
    path("profile/<str:userID>", v.profileView, name="Profile"),
    path("listing/add", v.addListingsView, name="Add Listing"),
    path("", v.indexView, name="Index"),
]   