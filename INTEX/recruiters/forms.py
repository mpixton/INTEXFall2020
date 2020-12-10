# pylint:disable=no-member

from django import forms
from recruiters.choices import SIZE, SECTOR
from seekers.models import ContractType, ContractLength, ListingSkill, Skill
from seekers.choices import SKILL_LEVEL
from django.forms import ValidationError


class PostJobForm(forms.Form) :
    """
    Form used to post a listing to the website. \n
    Fields: \n
    job_title -> Charfield \n
    job_description -> Charfield \n
    location -> CharField \n
    contract_type -> ModelChoiceField->ContractType \n
    contract_length -> ModelChoiceField->ContractLength \n
    """
    job_title = forms.CharField(label='Job Title')
    job_description = forms.CharField(label='Job Description', widget=forms.Textarea)
    location = forms.CharField(label='Location')
    contract_type = forms.ModelChoiceField(queryset=ContractType.objects.all().order_by('contract_type'), label='French Contract Type:')
    contract_length = forms.ModelChoiceField(queryset=ContractLength.objects.all().order_by('contract_length'), label='Contract Term:')
    salary_upper = forms.DecimalField(max_digits=8, label='What is the salary upper limit for this job?', decimal_places=2)
    salary_lower = forms.DecimalField(max_digits=8, label='What is the salary lower limit for this job?', decimal_places=2)
    reloc = forms.BooleanField(label='Relocation assistance available?', required=True)

    def clean_salary_lower(self) :
        sl =  self.cleaned_data.get('salary_lower')
        su = self.cleaned_data.get('salary_upper')
        if sl > su :
            raise ValidationError('The lower limit is not lower than the upper limit!')
        # need to return a value or it will be a none
        return self.cleaned_data.get('salary_lower')

class AddListingSkillForm(forms.Form) :
    """
    Form used to add a skill to a listing. \n
    Fields: \n
    skill -> ModelChoiceField->Skill \n
    level -> CharChoicesField->SKILL_LEVEL \n
    is_required -> BooleanField \n
    """
    skill = forms.ModelChoiceField(queryset=Skill.objects.all())
    level = forms.CharField(
        max_length=1,
        widget=forms.Select(choices=SKILL_LEVEL)
    )
    is_required = forms.BooleanField(label='Is required?', help_text='If left unchecked, it indicates that the skill is preferred.', required=False)