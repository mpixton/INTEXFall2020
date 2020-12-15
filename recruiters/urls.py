from django.urls import path
import recruiters.views as v
from seekers.views import loginView

app_name = 'Recruiters'
urlpatterns = [
    # path("applicant_listings", v.applicantListingsView, name="Applicant Listings"),
    path("listing/addListing", v.AddListingView, name="CreateJob"),
    path('listing/editListing/<str:ListingID>', v.EditListingView, name='EditListing'),
    path('listing/deleteListing/<str:ListingID>', v.DeleteListingView, name='DeleteListing'),
    path('listing/addSkill/<str:ListingID>', v.AddListingSkill, name='AddListingSkill'),
    path('listing/editSkill/<str:ListingSkillID>', v.EditListingSkillView, name='EditListingSkill'),
    path('listing/deleteSkill/<str:ListingSkillID>', v.DeleteListingSkillView, name='DeleteListingSkill'),
    path("listing/applicants", v.applicantsView, name="Applicants"),
    path('listing/login/', loginView, name='Login'),
]   