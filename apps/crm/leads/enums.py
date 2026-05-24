from django.db import models


class LeadStatus(models.TextChoices):
    NEW = 'new', 'New'
    CONTACTED = 'contacted', 'Contacted'
    QUALIFIED = 'qualified', 'Qualified'
    REJECTED = 'rejected', 'Rejected'

class LeadSource(models.TextChoices):
    WEBSITE = 'website', 'Webite'
    CALL = 'call', 'Call'
    EMAIL = 'email', 'Email'
    ADS = 'ads', 'Ads'