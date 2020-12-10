from django import forms
from seekers.models import Skill
from django.forms import ValidationError
from seekers.choices import ACCOUNT_TYPE, SKILL_LEVEL
from recruiters.choices import SECTOR, SIZE
from seekers.models import Seeker
import re


#disable no-member syntax error
# pylint:disable=no-member

class BaseSignUpForm(forms.Form) :
    """
    Abstract Form extended by Recruiter and Seeker SignUpForms.
    Fields: \n
    first_name -> CharField \n
    last_name -> CharField \n
    email -> EmailField \n
    username -> CharField \n
    password -> CharField(PasswordInput) \n
    repeat_password -> CharField(PasswordInput) \n
    """
    first_name = forms.CharField()
    last_name = forms.CharField()
    email = forms.EmailField()
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
    repeat_password = forms.CharField(widget=forms.PasswordInput)

    def clean_repeat_password(self) :
        if self.cleaned_data.get('password') != self.cleaned_data.get('repeat_password') :
            raise ValidationError('The passwords do not match!')

class RecruiterSignUpForm(BaseSignUpForm) :
    """
    Form to allow a Seeker to sign up for the website. \n
    Fields : \n
    email -> EmailField \n
    username -> CharField \n
    password -> CharField(PasswordWidget) \n
    repeat_password -> CharField(PasswordWidget) \n
    first_name -> CharField \n
    last_name -> CharField \n
    employee_job_title -> CharField \n
    org_name -> CharField \n
    """
    employee_job_title = forms.CharField(label='Your Job Title')
    org_name = forms.CharField()

    field_order = ['first_name', 'last_name', 'org_name', 'employee_job_title', 'email','username', 'password', 'repeat_password', 'phone']


class SeekerSignUpForm(BaseSignUpForm) :
    """
    Form to allow a Seeker to sign up for the website. \n
    Fields : \n
    email -> EmailField \n
    username -> CharField \n
    password -> CharField(PasswordWidget) \n
    repeat_password -> CharField(PasswordWidget) \n
    first_name -> CharField \n
    last_name -> CharField \n
    phone -> CharField \n
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
    Form to allow a user to login. \n
    Fields: \n
    username -> CharField \n
    password -> CharField(PasswordInput) \n
    """
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


class updateInfo(forms.Form) :
    newResume = forms.FileField()
    newSkill = forms.ModelChoiceField(Skill.objects.all())


class ListingSearch(forms.Form) :
    keyword = forms.CharField()


class AddSkillsForm(forms.Form) :
    """
    Form to add a skill to a user. \n
    Fields: \n
    skill -> ModelChoiceField(SkillObject) \n
    level -> ChoiceField(SKILL_LEVEL) \n
    """
    skill = forms.ModelChoiceField(Skill.objects.all())
    level = forms.ChoiceField(choices=SKILL_LEVEL)


class applyForm(forms.Form) :
    first_name = forms.CharField()
    last_name = forms.CharField()
    email = forms.EmailField()