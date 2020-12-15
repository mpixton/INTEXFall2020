"""
Forms used by the Recruiters app. 

Forms:
    PostJobForm: Allows a Recruiter to post Listings to the site.
    AddListingSkillForm: Allows a Recruiter to add Skills to a Listing.
"""
# Python Imports

# Django Imports
from django import forms
from django.forms import ValidationError
# App Imports
from recruiters.choices import SIZE, SECTOR
from seekers.choices import SKILL_LEVEL, RELOCATION_ASSISTANCE
from seekers.models import ContractType, ContractLength, ListingSkill, Skill

# pylint:disable=no-member

class PostJobForm(forms.Form) :
    """
    Used by Recruiters to post a Listing to the site. 

    Fields:
        job_title: Charfield 
        job_description: Charfield 
        location: CharField 
        contract_type: ModelChoiceField -> ContractType 
        contract_length: ModelChoiceField -> ContractLength 
        salary_upper: DecimalField(max_digits 8, decimal places 2)
        salary_lower: DecimalField(max_digits 8, decimal_places 2)
        reloc: CharField(choices RELOCATION_ASSISTANCE)
    """
    job_title = forms.CharField(label='Job Title')
    job_description = forms.CharField(label='Job Description', widget=forms.Textarea)
    location = forms.CharField(label='Location')
    contract_type = forms.ModelChoiceField(
        queryset=ContractType.objects.all().order_by('contract_type'), 
        label='French Contract Type:'
        )
    contract_length = forms.ModelChoiceField(
        queryset=ContractLength.objects.all().order_by('contract_length'), 
        label='Contract Term:'
        )
    salary_upper = forms.DecimalField(
        max_digits=8, 
        label='What is the salary upper limit for this job?', 
        decimal_places=2
        )
    salary_lower = forms.DecimalField(
        max_digits=8, 
        label='What is the salary lower limit for this job?', 
        decimal_places=2)
    reloc = forms.CharField(
        label='Relocation assistance available?', 
        widget=forms.Select(choices=RELOCATION_ASSISTANCE)
        )

    def clean_salary_lower(self) :
        sl =  self.cleaned_data.get('salary_lower')
        su = self.cleaned_data.get('salary_upper')
        if sl > su :
            raise ValidationError('The salary lower limit should be less than the upper limit!')
        # need to return a value or it will be a none
        return self.cleaned_data.get('salary_lower')

class AddListingSkillForm(forms.Form) :
    """
    Used by Recruiters to add a Skill to a Listing.

    Fields: 
        skill: ModelChoiceField->Skill 
        level: CharField(choices SKILL_LEVEL)
        is_required: BooleanField 
    """
    skill = forms.ModelChoiceField(queryset=Skill.objects.all().order_by('skill_name'))
    level = forms.CharField(
        max_length=1,
        widget=forms.Select(choices=SKILL_LEVEL)
        )
    is_required = forms.BooleanField(
        label='Is required?', 
        help_text='If left unchecked, it indicates that the skill is preferred.', 
        required=False
        )