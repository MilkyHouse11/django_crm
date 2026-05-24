from django.db import models
from django.core.exceptions import ValidationError
from ..leads.models import Lead
from ..deals.models import Deal
from django.contrib.auth import get_user_model

User = get_user_model()


class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    lead = models.ForeignKey(Lead, null=True, blank=True, on_delete=models.CASCADE, related_name="comments")
    deal = models.ForeignKey(Deal, null=True, blank=True, on_delete=models.CASCADE, related_name="comments")
    content = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.CheckConstraint(condition=models.Q(lead__isnull=False) | models.Q(deal__isnull=False),
                                   name="comment_deal_lead_validation")
        ]

    def __str__(self):
        return f"Comment by {self.author}"
    
    def clean(self):
        if not self.lead and not self.deal:
            raise ValidationError('Comment must have deal or lead')
        
        if self.lead and self.deal:
            raise ValidationError('Comment can have only lead or only deal')
        
        return super().clean()