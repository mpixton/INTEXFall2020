from django.urls import path
import recruiters.views as v

urlpatterns = [
    path("all", v.ShowingsPageView, name="All"),
    path("movie/<str:Film>", v.MoviePageView, name="Movie"),
    path("showing/<str:ShowingID>", v.ShowingDetailView, name="Showing"),
    path("", v.IndexPageView, name="Index"),
]   