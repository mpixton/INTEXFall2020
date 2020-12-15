"""
Contains all Django models for the Seekers app.

Models: 
    Seeker: a profile for Job Seeker user
    Skill: a Skill for either a Seeker or a Listing
    SeekerSkill: a Skill associated with a Seeker
    ContractType: contract type
    ContractLength: contract length 
    Listing: a job listing
    ListingSkill: a Skill associated with a Listing
    Application: an Seeker applying for a Listing
    JobOffer: an offer extended by a Recruiter to an Application
"""

# //TODO 
# Refactor out the seekers profile to a new Accounts app

# Python Imports
from datetime import datetime as DT
# Django Imports
from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
# App Imports
from recruiters.models import Recruiter
from seekers.choices import RELOCATION_ASSISTANCE, SKILL_LEVEL

# Create your models here.
# pylint:disable=no-member


# The User object is used by Django for auth. Has the first name, last name,
# username, email, and password fields. 
class Seeker(models.Model) :
    """
    Creates a profile for a Job Seeker, associated with a User account. 

    Allows storing additional information about a Job Seeker user, 
    such as their resume and phone number.

    Fields:
        user: OneToOne -> User, on_delete CASCADE
        has_resume: BooleanField
        phone: CharField, max_length 15
    """
    user = models.OneToOneField(to=User, on_delete=models.CASCADE)
    # has_resume currently replaces the resume file upload
    has_resume = models.BooleanField()
    phone = models.CharField(max_length=15)
    # resume = models.FileField(upload_to='uploads/', null=True)

    class Meta :
        # makes life easier by declaring job seeker accounts as such
        permissions = [
            ('is_seeker', 'Is a Job Seeker')
        ]

    def __str__(self):
        return str(self.user.get_full_name())

    def get_absolute_url(self):
        return reverse("Seekers:Profile", kwargs={'Type': 'seeker', "userID": self.pk})
    


class Skill(models.Model) :
    """
    Stores a list of skills, predetermined by us. 

    Lets us define a list of skills that Job Seekers can associate with
    their account and Recruiters can associate with their Listings.

    Fields:
        skill_name: CharField, max_length 30
    """
    skill_name = models.CharField(max_length=30)

    def __str__(self):
        return self.skill_name
    

class SeekerSkill(models.Model) :
    """
    Stores association between Seeker and Skill.

    Allows seekers to attach Skills to their account. Stores the 
    proficency level of the skill. Job Seekers are not allowed 
    to associate themselves with a skill more than once. 

    Fields:
        seeker: ForeignKey -> Seeker, on_delete DO_NOTHING
        skill: ForeignKey -> Skill, on_delete DO_NOTHING
        level: CharField, max_length 1, choices SKILL_LEVEL
    """
    seeker = models.ForeignKey(to=Seeker, on_delete=models.DO_NOTHING)
    skill = models.ForeignKey(to=Skill, on_delete=models.DO_NOTHING)
    level = models.CharField(max_length=1, choices=SKILL_LEVEL)

    class Meta: 
        unique_together = ('seeker', 'skill')

    def __str__(self):
        return str(self.seeker.user.get_full_name()) + ' ' + str(self.skill) + ' ' + str(self.level)
    

class ContractType(models.Model) :
    """
    Stores contract types.

    Stores French contract types. Allows us to define the contract 
    types available for Recruiters to list.

    Fields:
        contract_length: CharField, max_length 30
    """
    contract_type = models.CharField(max_length=30)

    def __str__(self):
        return self.contract_type
    

class ContractLength(models.Model) :
    """
    Stores contract lengths.

    Stores contract lengths. Allows us to define the contract terms. 

    Fields:
        contract_length: CharField, max_length 10, unique True
    """
    contract_length = models.CharField(max_length=10, unique=True)

    def __str__(self) :
        return str(self.contract_length) + ' months'


class Listing(models.Model) :
    """
    A job posting, as created by a Recruiter.

    Stores a job opening at a Recruiter's organization. Allows Job 
    Seekers to seearch for jobs, and Recruiters to sift through 
    applicants to find qualifed candidates.

    Fields:
        posted_by: ForeignKey -> Recruiter, on_delete DO_NOTHING
        listing_job_title: CharField, max_length 50
        job_description: TextField
        location: CharField, max_length 50
        contract_type: ForeignKey -> ContractType, on_delete DO_NOTHING
        contract_length: ForeignKey -> ContractLength, on_delete DO_NOTHING
        salary_upper: DecimalField, max_digits 8, decimal_places 2
        salary_lower: DecimalField, max_digits 8, decimal_places 2
        relocation_assistance: CharField, max_length 1, choices RELOCATION_ASSISTANCE
    """
    posted_by = models.ForeignKey(to=Recruiter, on_delete=models.DO_NOTHING)
    listing_job_title = models.CharField(max_length=50)
    job_description = models.TextField()
    location = models.CharField(max_length=50)
    contract_type = models.ForeignKey(to=ContractType, on_delete=models.DO_NOTHING, null=True)
    contract_length = models.ForeignKey(to=ContractLength, on_delete=models.DO_NOTHING, null=True)
    salary_upper = models.DecimalField(max_digits=8, decimal_places=2)
    salary_lower = models.DecimalField(max_digits=8, decimal_places=2)
    relocation_assistance = models.CharField(max_length=1, verbose_name='Relocation Assistance Available?', choices=RELOCATION_ASSISTANCE)

    def __str__(self):
        return str(self.posted_by.org) + ' ' + str(self.listing_job_title)

    # //TODO Set abs URL
    # def get_absolute_url(self):
    #     return reverse("model_detail", kwargs={"pk": self.pk})


class ListingSkill(models.Model) :
    """
    Stores association between a Skill and a Listing.

    Allows Recruiters to associate Skills with a Listing. Recruiters 
    may mark them as Required or Preferred. Also allows Recruiters to 
    set the expertise level desired in the Skill.

    Fields:
        listing: ForeignKey -> Listing, on_delete DO_NOTHING
        skill: ForeignKey -> Skill, on_delete DO_NOTHING
        level: CharField, max_length 1, choices SKILL_LEVEL
        is_required: BooleanField
    """
    listing = models.ForeignKey(to=Listing, on_delete=models.DO_NOTHING)
    skill = models.ForeignKey(to=Skill, on_delete=models.DO_NOTHING)
    level = models.CharField(max_length=1, choices=SKILL_LEVEL)
    is_required = models.BooleanField()

    class Meta: 
        unique_together = ('skill', 'listing')


    def __str__(self) :
        return str(self.listing) + ' ' + str(self.skill) + ' ' + self.level

# TODO
# Add a matching skills?
class Application(models.Model) :
    """
    Stores a Job Seeker applying to a Listing.

    Allows Job Seekers to apply to a job, and Recruiters to sift
    through the candidate pool.

    Fields:
        seeker: ForeignKey -> Seeker, on_delete DO_NOTHING
        listing: ForeignKey -> Listing, on_delete SET_NULL
    """
    seeker = models.ForeignKey(to=Seeker, on_delete=models.DO_NOTHING)
    listing = models.ForeignKey(to=Listing, on_delete=models.SET_NULL, null=True)
    _date_applied = models.DateField()

    class Meta: 
        unique_together = ('seeker', 'listing')

    def __str__(self):
        return str(self.seeker.user) + ' ' + str(self.listing)

    def save(self, *args, **kwargs) :
        self.date_applied = DT.now().date()  
        super(Application, self).save(*args, **kwargs)

    # //TODO
    # def get_absolute_url(self):
    #     return reverse("model_detail", kwargs={"pk": self.pk})
    

class JobOffer(models.Model) :
    """
    Allows Recruiters to extend an offer to an Applicant.

    Links a Recruiter to an Application, and by consequence, a Job Seeker. 

    Fields:
        extended_by: ForeignKey -> Recruiter, on_delete DO_NOTHING
        extended_to: ForeignKey -> Application, on_delete DO_NOTHING
        offer_job_title: CharField, max_length 50
        is_accepted: BooleanField
    """
    extended_by = models.ForeignKey(to=Recruiter, on_delete=models.DO_NOTHING)
    extended_to = models.OneToOneField(to=Application, on_delete=models.DO_NOTHING)
    offer_job_title = models.CharField(max_length=50)
    is_accepted = models.BooleanField()
    # //TODO
    # Add offer salary, offer date, date accepted
    
    def __str__(self):
        return str(self.person) + ' ' + str(self.offerJobTitle)

    # //TODO
    # def get_absolute_url(self):
    #     return reverse("model_detail", kwargs={"pk": self.pk})
    