from django import template
from seekers.choices import SKILL_LEVEL

register = template.Library()

# takes the rating level numeric value and returns the human-readable string
def returnRating(value) :
    for skill in SKILL_LEVEL :
        if str(skill[0]) == str(value) :
            return skill[1]

register.filter('returnRating', returnRating)