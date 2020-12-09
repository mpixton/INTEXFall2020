from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import datetime as DT
from recruiters.models import Recruiter
from seekers.choices import SKILL_LEVEL
from django.contrib.auth.models import User

# Create your models here.
# pylint:disable=no-member


# The User object is used by Django for auth. Has the first name, last name, username, email, and password fields. 
class Seeker(models.Model) :
    """
    Model for a Job Seeker. Stores extra information about a User specfic to a Seeker.
    """
    user = models.OneToOneField(to=User, on_delete=models.CASCADE)
    has_resume = models.BooleanField()
    phone = models.CharField(max_length=14)
    resume = models.FileField(upload_to='uploads/', null=True)

    def __str__(self):
        return str(self.user.get_full_name()) + ' seeker'

    class Meta :
        permissions = [
            ('is_seeker', 'Is a job seeker user')
        ]


class Skill(models.Model) :
    """
    Model for a skill. Allows the Job Seeker and Recruiter to speak a common lingo for skills.
    """
    skill_name = models.CharField(max_length=30)

    def __str__(self):
        return self.skill_name
    

class SeekerSkill(models.Model) :
    """
    Model for a Job Seeker-Skill-level instance. Allows the Job Seeker to have a Skill and level for that skill. 0 is not allowed because then its not a skill. A Job Seeker-Skill pairing must be unique. 
    """
    seeker = models.ForeignKey(to=Seeker, on_delete=models.DO_NOTHING)
    skill = models.ForeignKey(to=Skill, on_delete=models.DO_NOTHING)
    level = models.CharField(max_length=1, choices=SKILL_LEVEL)

    def __str__(self):
        return str(self.seeker.user.get_full_name()) + ' ' + str(self.skill) + ' ' + str(self.level)
    
    class Meta: 
        unique_together = ('seeker', 'skill')


class ContractType(models.Model) :
    """
    Model for a Contract Type, according to French standards.
    """
    contract_type = models.CharField(max_length=30)

    def __str__(self):
        return self.contract_type
    

class ContractLength(models.Model) :
    """
    Model for Contract Lengths. 
    """
    contract_length = models.IntegerField(null=True, blank=True)

    def __str__(self) :
        return str(self.contract_length) + ' months'


class Listing(models.Model) :
    """
    Model for a Listing. Created by a Recruiter, affliated with an Organization. Allows Seekers to apply for employment at an Organization.
    """
    posted_by = models.ForeignKey(to=Recruiter, on_delete=models.DO_NOTHING)
    listing_job_title = models.CharField(max_length=50)
    job_description = models.TextField()
    location = models.CharField(max_length=50)
    contract_type = models.ForeignKey(to=ContractType, on_delete=models.DO_NOTHING, null=True)
    contract_length = models.ForeignKey(to=ContractLength, on_delete=models.DO_NOTHING, null=True)

    def __str__(self):
        return str(self.posted_by.org) + ' ' + str(self.listing_job_title)

    # def get_absolute_url(self):
    #     return reverse("model_detail", kwargs={"pk": self.pk})


class ListingSkill(models.Model) :
    """
    Model for a ListingSkill. Allows a recruiter to supply skills that are required or recommended for the posting.
    """
    listing = models.ForeignKey(to=Listing, on_delete=models.DO_NOTHING)
    skill = models.ForeignKey(to=Skill, on_delete=models.DO_NOTHING)
    level = models.CharField(max_length=1, choices=SKILL_LEVEL)
    is_required = models.BooleanField()

    def __str__(self) :
        return str(self.listing) + ' ' + str(self.skill) + ' ' + self.level
        

class Application(models.Model) :
    """
    Model for an Application. Do not allow the user to specify the date_applied date. The system will handle it.
    """
    seeker = models.ForeignKey(to=Seeker, on_delete=models.DO_NOTHING)
    listing = models.ForeignKey(to=Listing, on_delete=models.DO_NOTHING)
    date_applied = models.DateField()

    def __str__(self):
        return str(self.seeker.user) + ' ' + str(self.listing)

    def save(self, *args, **kwargs) :
        self.date_applied = DT.now().date()  
        super(Application, self).save(*args, **kwargs)
    
    class Meta: 
        unique_together = ('seeker', 'listing')

    # def get_absolute_url(self):
    #     return reverse("model_detail", kwargs={"pk": self.pk})
    

class JobOffer(models.Model) :
    """
    Model for an Offer. Created by a Recruiter, affliated with an Organization. Sent to a Job Seeker.
    """
    extended_by = models.ForeignKey(to=Recruiter, on_delete=models.DO_NOTHING)
    extended_to = models.OneToOneField(to=Application, on_delete=models.DO_NOTHING)
    offer_job_title = models.CharField(max_length=50)
    contract = models.CharField(max_length=30)
    is_accepted = models.BooleanField()
    salary_upper = models.DecimalField(max_digits=8, decimal_places=2)
    salary_lower = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return str(self.person) + ' ' + str(self.offerJobTitle)

    # def get_absolute_url(self):
    #     return reverse("model_detail", kwargs={"pk": self.pk})
    