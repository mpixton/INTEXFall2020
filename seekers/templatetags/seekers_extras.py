from django import template
from seekers.choices import SKILL_LEVEL, RELOCATION_ASSISTANCE

register = template.Library()

# takes the rating level numeric value and returns the human-readable string
def returnRating(value) :
    for skill in SKILL_LEVEL :
        if str(skill[0]) == str(value) :
            return skill[1]

register.filter('returnRating', returnRating)

# takes the relocation assistance and returns the human-readable string
def returnReloc(value) :
    for ra in RELOCATION_ASSISTANCE :
        if str(ra[0]) == str(value) :
            return ra[1]

register.filter('returnReloc', returnReloc)