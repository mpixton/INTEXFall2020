# pylint:disable=no-member

from django import forms
from recruiters.choices import SIZE, SECTOR
from seekers.models import ContractType, ContractLength

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

class PostJobForm(forms.Form) :
    job_title = forms.CharField(label='Job Title')
    job_description = forms.CharField(label='Job Description')
    location = forms.CharField(label='Location')
    contract_length = forms.ModelChoiceField(queryset=ContractLength.objects.all())
    contract_type = forms.ModelChoiceField(queryset=ContractType.objects.all())