from django.db import models
from django.core.exceptions import ValidationError


class Team(models.Model):
    name = models.CharField(max_length=50)
    company = models.ForeignKey('companies.Company', related_name='teams', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.company}: {self.name}"
    
    def clean(self, *args, **kwargs):
        if self.company_id and self.company.teams.filter(name__iexact=self.name):
            raise ValidationError('A team with this name already exists in this company')
        
        return super().clean(*args, **kwargs)