from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import datetime as DT
from recruiters.models import Organization, Recruiter
from seekers.choices import SKILL_LEVEL
from django.contrib.auth.models import User

# Create your models here.
# pylint:disable=no-member


class Person(models.Model) :
    """
    Model for a person. Job Seekers and Recruiters inherit from this class.
    """
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField()
    username = models.CharField(max_length=30, unique=True)
    user = models.OneToOneField(to=User, on_delete=models.CASCADE)

    class Meta:
        abstract = True

    def __str__(self):
        return self.first_name + ' ' + self.last_name


class Seeker(Person) :
    """
    Model for a Job Seeker. Inherits from Person. 
    """
    has_resume = models.BooleanField()

    def __str__(self):
        return str(self.person) + ' seeker'


class Skill(models.Model) :
    """
    Model for a skill. Allows the Job Seeker and Recruiter to speak a common lingo for skills.
    """
    skill_name = models.CharField(max_length=30)

    def __str__(self):
        return self.skill_name
    

class SeekerSkills(models.Model) :
    """
    Model for a Job Seeker-Skill-level instance. Allows the Job Seeker to have a Skill and level for that skill. 0 is not allowed because then its not a skill. A Job Seeker-Skill pairing must be unique. 
    """
    seeker = models.ForeignKey(to=Seeker, on_delete=models.DO_NOTHING)
    skill = models.ForeignKey(to=Skill, on_delete=models.PROTECT)
    level = models.IntegerField(choices=SKILL_LEVEL)

    def __str__(self):
        return str(self.seeker.person) + ' ' + str(self.skill) + ' ' + self.level
    
    class Meta: 
        unique_together = ('seeker', 'skill')


class Listing(models.Model) :
    """
    Model for a Listing. Created by a Recruiter, affliated with an Organization. Allows Seekers to apply for employment at an Organization.
    """
    organization = models.OneToOneField(to=Organization, on_delete=models.CASCADE)
    listingJobTitle = models.CharField(max_length=50)
    jobDescription = models.TextField()

    def __str__(self):
        return str(self.organization) + ' ' + str(self.listingJobTitle)

    # def get_absolute_url(self):
    #     return reverse("model_detail", kwargs={"pk": self.pk})


class ContractType(models.Model) :
    """
    Model for a Contract Type, according to French standards.
    """
    contract_type = models.CharField(max_length=30)
    contract_length = models.IntegerField(null=True, blank=True)


class Application(models.Model) :
    """
    Model for an Application. Do not allow the user to specify the date_applied date. The system will handle it.
    """
    seeker = models.ForeignKey(to=Seeker, on_delete=models.DO_NOTHING)
    listing = models.ForeignKey(to=Listing, on_delete=models.DO_NOTHING)
    date_applied = models.DateField()

    def __str__(self):
        return str(self.seeker.person) + ' ' + str(self.listing)

    def save(self, *args, **kwargs) :
        self.date_applied = DT.now().date()  
        super(Application, self).save(*args, **kwargs)

    # def get_absolute_url(self):
    #     return reverse("model_detail", kwargs={"pk": self.pk})
    

class JobOffer(models.Model) :
    """
    Model for an Offer. Created by a Recruiter, affliated with an Organization. Sent to a Job Seeker.
    """
    extended_by = models.ForeignKey(to=Recruiter, on_delete=models.DO_NOTHING)
    extended_to = models.OneToOneField(to=Application, on_delete=models.DO_NOTHING)
    offer_job_title = models.CharField(max_length=50)
    organization = models.OneToOneField(to=Organization, on_delete=models.CASCADE)
    contract = models.CharField(max_length=30)
    is_accepted = models.BooleanField()
    salary_upper = models.DecimalField(max_digits=8, decimal_places=2)
    salary_lower = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return str(self.person) + ' ' + str(self.offerJobTitle)

    # def get_absolute_url(self):
    #     return reverse("model_detail", kwargs={"pk": self.pk})
    