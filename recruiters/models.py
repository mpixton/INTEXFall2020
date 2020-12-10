from django.db import models
from recruiters.choices import SECTOR, SIZE
from django.contrib.auth.models import User

# Create your models here.
# pylint:disable=no-member


class Recruiter(models.Model) :
    """
    Model for a Recruiter. Affliated with an organization.
    """
    user = models.OneToOneField(to=User, on_delete=models.CASCADE)
    org = models.CharField(verbose_name='Organization', max_length=100)
    emp_job_title = models.CharField(max_length=50, verbose_name='Employee Job Title')
    
    def __str__(self):
        return str(self.user.get_full_name()) + ' recruiter'

    class Meta :
        permissions= [
            ('is_recruiter', 'Is a Recruiter')
        ]