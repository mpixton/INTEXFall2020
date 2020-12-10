from django.urls import path
import seekers.views as v  

app_name = 'Seekers'
urlpatterns = [
    path("job_listings", v.jobListingsView, name="JobListings"),
    path("profile/<str:Type>/<str:userID>", v.profileView, name="Profile"),
    path("apply/<str:ListingID>", v.applicationView, name="Application"),
    # path("search", v.searchJob, name="Search"),
    # path('results', v.SearchResultsView, name='SearchResults'),
    path("create_account/<str:AccountType>", v.CreateAccountView, name="CreateAccount"),
    path("login", v.loginView, name="Login"),
    path("logout", v.logoutView,name="Logout"),
    path("about", v.about, name ="About"),
    path("add_skills", v.AddSeekerSkillsView, name="AddSkills"),
    path('editSkills/<str:SeekerSkillID>', v.EditSeekerSkillsView, name='EditSkills'),
    path('deleteSkills/<str:SeekerSkillID>', v.DeleteSeekerSkillsView, name='DeleteSkills'),
    path("search_bar/<str:SearchString>", v.SearchBar, name="SearchBar"),
    path("userApplications", v.userApplicationsView, name="UserApplication"),
    path("trending_jobs", v.recommenderDisplayView, name="TrendingJobs"),
    path("learn_more", v.learnMoreView, name="LearnMore"),
    path("", v.IndexPageView, name="Index"),
]   