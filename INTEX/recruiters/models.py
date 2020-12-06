from django.db import models
from recruiters.choices import SECTOR, SIZE

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

    class Meta:
        abstract = True

    def __str__(self):
        return self.first_name + ' ' + self.last_name


class Organization(models.Model) :
    """
    Model for an organization. Employs Recruiters. 
    """
    org_name = models.CharField(max_length=100, verbose_name='Organization Name')
    size = models.CharField(max_length=2, choices=SIZE)
    sector = models.CharField(max_length=2, choices=SECTOR)
    
    def __str__(self):
        return str(self.person) + ' org'


class Recruiter(Person) :
    """
    Model for a Recruiter. Affliated with an organization.
    """
    org = models.OneToOneField(to=Organization, on_delete=models.CASCADE, verbose_name='Organization Name')
    emp_job_title = models.CharField(max_length=50, verbose_name='Employee Job Title')
    
    def __str__(self):
        return str(self.person) + ' recruiter'