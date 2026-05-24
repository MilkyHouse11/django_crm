from django.db import models
from django.core.exceptions import ValidationError


class Membership(models.Model):
    team = models.ForeignKey('teams.team', null=True, on_delete=models.SET_NULL)
    company = models.ForeignKey('companies.company', null=True, on_delete=models.SET_NULL)
    user = models.OneToOneField('users.user', on_delete=models.CASCADE)

    def clean(self):
        if self.team.company != self.company:
            raise ValidationError('Team company and membership company must be same')

        return super().clean()