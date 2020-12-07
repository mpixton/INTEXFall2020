from django import forms
from recruiters.choices import SIZE, SECTOR

class CreateOrgForm(forms.Form) :
    org_name = forms.CharField(label='Organization Name')
    size = forms.CharField(
        max_length=2,
        widget=forms.Select(choices=SIZE)
    )
    sector = forms.CharField(
        max_length=2,
        widget=forms.Select(choices=SECTOR)
    )

class PostJob(forms.Form) :
    job_title = 
    organization = forms.CharField(label='Organization Name')
    listingJobTitle = forms.
    jobDescription = models.TextField()