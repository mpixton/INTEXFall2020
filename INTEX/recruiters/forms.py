# pylint:disable=no-member

from django import forms
from recruiters.choices import SIZE, SECTOR
from seekers.models import ContractType, ContractLength, ListingSkill, Skill
from seekers.choices import SKILL_LEVEL


# //TODO Refactor out of code base (rendered obsolete when Organization was removed as an object)
class CreateOrgForm(forms.Form) :
    """
    Form used to create an Organization.
    """
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
    """
    Form used to post a listing to the website. \n
    Fields: job_title (Charfield), job_description (Charfield), location (CharField), contract_type (ModelChoiceField->ContractType), contract_length (ModelChoiceField->ContractLength)
    """
    job_title = forms.CharField(label='Job Title')
    job_description = forms.CharField(label='Job Description', widget=forms.Textarea)
    location = forms.CharField(label='Location')
    contract_type = forms.ModelChoiceField(queryset=ContractType.objects.all(), label='French Contract Type:')
    contract_length = forms.ModelChoiceField(queryset=ContractLength.objects.all(), label='Contract Term:')

class AddListingSkillForm(forms.Form) :
    """
    Form used to add a skill to a listing. \n
    Fields: skill (ModelChoiceField->Skill), level (CharChoicesField->SKILL_LEVEL), is_required (BooleanField)
    """
    skill = forms.ModelChoiceField(queryset=Skill.objects.all())
    level = forms.CharField(
        max_length=1,
        widget=forms.Select(choices=SKILL_LEVEL)
    )
    is_required = forms.BooleanField(label='Is required?', help_text='If left unchecked, it indicates that the skill is preferred.', required=False)