"""
Models for the Recruiters app.

Models:
    Recruiter: profile for a Recruiter User
"""
# Python Imports

# Django Imports
from django.db import models
from django.contrib.auth.models import User
# App Imports
from recruiters.choices import SECTOR, SIZE

# pylint:disable=no-member

class Recruiter(models.Model) :
    """
    Profile for a Recruiter user.
    
    Posts jobs, sorts through Job Seekers, and extends offers.

    Attributes: 
        user: OneToOne -> User, on_delete CASCADE
        org: CharField(max_length 100)
        emp_job_title: CharField(max_length 50)
    """
    user = models.OneToOneField(to=User, on_delete=models.CASCADE)
    org = models.CharField(verbose_name='Organization', max_length=100)
    emp_job_title = models.CharField(verbose_name='Employee Job Title', max_length=50)
    class Meta :
        # makes life easier by allowing a simple permission test
        permissions= [
            ('is_recruiter', 'Is a Recruiter')
        ]
    
    def __str__(self):
        return str(self.user.get_full_name())