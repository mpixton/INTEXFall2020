from django.urls import path
import recruiters.views as v

app_name = 'Recruiters'
urlpatterns = [
    # path("applicant_listings", v.applicantListingsView, name="Applicant Listings"),
    path("listing/add", v.postJobView, name="PostJob"),
    path("listing/post", v.createJobPostingView, name="CreateJob"),
    path("", v.indexView, name="Index"),
]   