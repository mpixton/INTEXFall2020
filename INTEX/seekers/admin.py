from django.contrib import admin

# Register your models here.
import seekers.models as s

admin.site.register(s.Listing)
admin.site.register(s.ContractLength)
admin.site.register(s.ContractType)
admin.site.register(s.Skill)