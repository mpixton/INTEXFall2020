from django import forms
from seekers.models import Skill
from django.forms import ValidationError
from seekers.choices import ACCOUNT_TYPE, SKILL_LEVEL
from recruiters.choices import SECTOR, SIZE
from seekers.models import Seeker
from recruiters.models import Organization


#disable no-member syntax error
# pylint:disable=no-member

class BaseSignUpForm(forms.Form) :
    email = forms.EmailField()
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
    repeat_password = forms.CharField(widget=forms.PasswordInput)

    def clean_repeat_password(self) :
        if self.cleaned_data.get('password') != self.cleaned_data.get('repeat_password') :
            raise ValidationError('The passwords do not match!')

class PersonSignUpForm(BaseSignUpForm) :
    first_name = forms.CharField()
    last_name = forms.CharField()

class RecruiterSignUpForm(PersonSignUpForm) :
    employee_job_title = forms.CharField()
    org_name = forms.ModelChoiceField(queryset=Organization.objects.all())

    field_order = ['first_name', 'last_name', 'employee_job_title', 'email','username', 'password', 'repeat_password', 'phone']

class SeekerSignUpFrom(PersonSignUpForm) :
    phone = forms.CharField(max_length=14, required=False)
    # resume = forms.FileField()
    # skill = forms.ModelChoiceField(Skill.objects.all())

    field_order = ['first_name', 'last_name', 'phone', 'email','username', 'password', 'repeat_password', 'phone'] 
class OrganizationSignUpForm(BaseSignUpForm) :
    org_name = forms.CharField(label='Organization Name')
    size = forms.CharField(
        max_length=2,
        widget=forms.Select(choices=SIZE)
    )
    sector = forms.CharField(
        max_length=2,
        widget=forms.Select(choices=SECTOR)
    )

    field_order = ['org_name', 'email', 'size', 'sector', 'username', 'password', 'repeat_password']

class LoginForm(forms.Form) :
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

class updateInfo(forms.Form) :
    newResume = forms.FileField()
    newSkill = forms.ModelChoiceField(Skill.objects.all())

class ListingSearch(forms.Form) :
    keyword = forms.CharField()

class AddSkillsForm(forms.Form) :
    skill = forms.ModelChoiceField(Skill.objects.all())
    level = forms.ChoiceField(choices=SKILL_LEVEL)

class applyForm(forms.Form) :
    first_name = forms.CharField()
    last_name = forms.CharField()
    email = forms.EmailField()

# class postJob(forms.Form) :
#     organization = forms.CharField()
#     listing_job_title = forms.CharField()
#     job_description = forms.CharField()
#     location = forms.CharField()
#     contract_type = forms.ChoiceField(choices=CONTRACT)

    