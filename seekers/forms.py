"""
Defines the forms used by the Seekers app.

Forms:
    RecruitersSignUpForm: allows an Anonymous User to sign up for a Recruiter account
    SeekersSignUpForm: allows an Anonymous User to sign up for a Job Seeker account
    LoginForm: allows a User to login 
    updateInfo: allows a Job Seeker to udpate their resume
    ListingSearch: allows a User to search Listings
    AddSkillsForm: allows a Job Seeker to add Skills to their profile
    applyForm: allows a Job Seeker to apply for a Listing
"""

# Python Imports
import re
# Django Imports
from django import forms
# App Imports
from recruiters import choices as rc
from seekers import choices as sc
from seekers import models as sm

#disable no-member syntax error
# pylint:disable=no-member

class _BaseSignUpForm(forms.Form) :
    """
    Base form used by Recruiter and SeekerSignUpForms.
    
    Contains common fields to both. Allows a User of the website to sign up as 
    either a Seeker or a Recruiter. Should not be used alone.

    Fields:
        first_name: CharField 
        last_name: CharField 
        email: EmailField 
        username: CharField 
        password: CharField(PasswordInput) 
        repeat_password: CharField(PasswordInput) 
    """
    first_name = forms.CharField()
    last_name = forms.CharField()
    email = forms.EmailField()
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
    repeat_password = forms.CharField(widget=forms.PasswordInput)

    def clean_repeat_password(self) :
        if self.cleaned_data.get('password') != self.cleaned_data.get('repeat_password') :
            raise forms.ValidationError('The passwords do not match!')

class RecruiterSignUpForm(_BaseSignUpForm) :
    """
    Provides a Recruiter a way to sign up for an account.

    Fields : 
        email: EmailField 
        username: CharField 
        password: CharField(PasswordWidget) 
        repeat_password: CharField(PasswordWidget) 
        first_name: CharField 
        last_name: CharField 
        employee_job_title: CharField 
        org_name: CharField 
    """
    employee_job_title = forms.CharField(label='Your Job Title')
    org_name = forms.CharField()

    field_order = ['first_name', 'last_name', 'org_name', 'employee_job_title', 'email','username', 'password', 'repeat_password']


class SeekerSignUpForm(_BaseSignUpForm) :
    """
    Provides a Seeker a way to sign up for an account.

    Fields : 
        email: EmailField 
        username: CharField 
        password: CharField(PasswordWidget) 
        repeat_password: CharField(PasswordWidget) 
        first_name: CharField 
        last_name: CharField 
        phone: CharField 
    """
    phone = forms.CharField(max_length=15, required=False)
    # resume = forms.FileField(label='Resume')
    # skill = forms.ModelChoiceField(Skill.objects.all())

    # def clean_phone(self) :
    #     if self.cleaned_data.get('phone') is None :
    #         return
    #     match = re.search('^\d{15}$', self.cleaned_data.get('phone'))
    #     if match is None :
    #         raise ValidationError(message='The phone number you provided is not valid.')

    field_order = ['first_name', 'last_name', 'phone', 'email','username', 'password', 'repeat_password'] 


class LoginForm(forms.Form) :
    """
    Allows logging into the site.

    Fields: 
        username: CharField 
        password: CharField(PasswordInput) 
    """
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

# //TODO FUTURE 
# Gives Job Seekers a way to update thier info
class updateInfo(forms.Form) :
    """
    Form to allow a Job Seeker to upload a new resume. 

    Fields: 
        newResume: FileField 
    """
    newResume = forms.FileField()


class ListingSearch(forms.Form) :
    """
    Allows a User to search site Listings.

    Fields: 
        keyword: CharField 
    """
    keyword = forms.CharField()


class AddSkillsForm(forms.Form) :
    """
    Adds a skill to a Seeker.

    Fields: 
        skill: ModelChoiceField -> SkillObject 
        level: ChoiceField, choices SKILL_LEVEL 
    """
    skill = forms.ModelChoiceField(sm.Skill.objects.all())
    level = forms.ChoiceField(choices=sc.SKILL_LEVEL)


class applyForm(forms.Form) :
    """
    Allows a Seeker to apply for a Listing.

    Fields: 
        first_name: CharField 
        last_name: CharField 
        email: EmailField 
    """
    first_name = forms.CharField()
    last_name = forms.CharField()
    email = forms.EmailField()