from django import forms
from seekers.models import Skill


class SignUpForm(forms.Form) :
    first_name = forms.CharField()
    last_name = forms.CharField()
    email = forms.EmailField(max_length = 254, required=True)
    password = forms.CharField(widget=forms.PasswordInput)
    resume = forms.FileField()
    skill = forms.ModelChoiceField(Skill.objects.all())
    phone = forms.CharField(max_length=10, required=False)

class updateInfo(forms.Form) :
    newResume = forms.FileField()
    resume = newResume
    newSkill = forms.ModelChoiceField(Skill.objects.all())
    skill = newSkill

class ListingSearch(forms.Form) :
    keyword = forms.CharField()




