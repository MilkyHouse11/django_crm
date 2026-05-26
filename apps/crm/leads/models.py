from django.db import models
from .enums import LeadStatus, LeadSource
from django.contrib.auth import get_user_model
from phonenumber_field.modelfields import PhoneNumberField

User = get_user_model()


class Lead(models.Model):
    full_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    phone = PhoneNumberField(unique=True)
    source = models.CharField(max_length=20, choices=LeadSource.choices)
    status = models.CharField(max_length=10, choices=LeadStatus.choices, default=LeadStatus.NEW)
    assigned_to = models.ForeignKey(User, blank=True, null=True, on_delete=models.DO_NOTHING, related_name="assigned_leads")
    created_by = models.ForeignKey(User, null=True, on_delete=models.DO_NOTHING, related_name="created_leads")
    team = models.ForeignKey(on_delete=models.DO_NOTHING, related_name='leads', to='teams.team')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.CheckConstraint(condition=models.Q(source__in=LeadSource.values), name="lead_source_validation"),
            models.CheckConstraint(condition=models.Q(status__in=LeadStatus.values), name="lead_status_validation"),
        ]

    def __str__(self):
        return self.full_name