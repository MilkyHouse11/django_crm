from django.db import models


class DealStage(models.TextChoices):
    NEGOTIAION = 'negotiation', 'Negotiation'
    PROPOSAL = 'proposal', 'Proposal'
    WON = 'won', 'Won'
    LOST = 'lost', 'Lost'