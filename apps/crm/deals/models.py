from django.db import models
from ..leads.enums import LeadStatus
from .enums import DealStage
from ..leads.models import Lead
from django.db.models import F
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime


class Deal(models.Model):
    lead = models.ForeignKey(
        Lead, on_delete=models.CASCADE, related_name="deals")
    title = models.CharField(max_length=50)
    expected_amount = models.PositiveIntegerField()
    actual_amount = models.PositiveIntegerField(null=True, blank=True)
    stage = models.CharField(
        max_length=50, choices=DealStage.choices, default=DealStage.NEGOTIAION)
    probability = models.PositiveIntegerField()
    expected_close_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    closed_stages = [DealStage.WON, DealStage.LOST]

    class Meta:
        constraints = [
            models.CheckConstraint(condition=models.Q(
                probability__range=(0, 100)), name="probability_range_0_100"),
            models.CheckConstraint(condition=models.Q(
                stage__in=DealStage.values), name='stage_valid_values'),
            models.CheckConstraint(condition=models.Q(
                closed_at__gte=F('created_at')), name='closed_after_creation')
        ]

    def __str__(self):
        return self.title

    def clean(self, *args, **kwargs):
        if not self.lead.is_active:
            raise ValidationError({'lead': 'You can not create deal with inactive lead'})
        
        if self.lead.status != LeadStatus.QUALIFIED:
            raise ValidationError({'lead': 'Lead status must be qualified'})

        closed_deal = self.stage in self.closed_stages

        if closed_deal:
            if self.stage == DealStage.WON and not self.actual_amount:
                    raise ValidationError({'actual_amount': 'Won deal must have actual amount'})
            elif self.stage == DealStage.LOST and self.actual_amount:
                    raise ValidationError(
                        'Losted deal couldn`t have actual amount')

        if self.probability > 100 or self.probability < 0:
            raise ValidationError({'probability': 'Probability must be between 0 and 100'})
        
        if self.pk:
            old_stage = Deal.objects.get(pk=self.pk).stage
        
            if DealStage.values.index(old_stage) > DealStage.values.index(self.stage):
                raise ValidationError({
                    'stage': "The deal stage cannot be updated to a previous stage."
                })
            
        else:
            if self.expected_close_date and self.expected_close_date < datetime.now().date():
                raise ValidationError({'expected_close_date': "Expected close date can't be less than now"})

        return super().clean(*args, **kwargs)

    def save(self, *args, **kwargs):
        is_new = self.pk is None

        if self.stage in self.closed_stages:
            if is_new:
                super().save()
                self.refresh_from_db()
                self.closed_at = timezone.now()
                super().save(update_fields=['closed_at'])
                return
            else:
                self.closed_at = timezone.now()
        else:
            self.closed_at = None

        return super().save(*args, **kwargs)