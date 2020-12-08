from django.db import models
from recruiters.choices import SECTOR, SIZE
from django.contrib.auth.models import User

# Create your models here.
# pylint:disable=no-member


class Organization(models.Model) :
    """
    Model for an organization. Employs Recruiters. 
    """
    user = models.OneToOneField(to=User, on_delete=models.CASCADE)
    org_name = models.CharField(max_length=100, verbose_name='Organization Name')
    size = models.IntegerField(choices=SIZE)
    sector = models.IntegerField(choices=SECTOR)
    
    def __str__(self):
        return str(self.org_name) + ' org'


# The User object is used by Django for auth. Has the first name, last name, username, email, and password fields. 
class Recruiter(models.Model) :
    """
    Model for a Recruiter. Affliated with an organization.
    """
    user = models.OneToOneField(to=User, on_delete=models.CASCADE)
    org = models.ForeignKey(to=Organization, on_delete=models.CASCADE, verbose_name='Organization Name')
    emp_job_title = models.CharField(max_length=50, verbose_name='Employee Job Title')
    
    def __str__(self):
        return str(self.user.get_full_name()) + ' recruiter'