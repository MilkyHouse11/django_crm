from django.test import TestCase, Client
from .models import Lead, Deal
from .enums import DealStage
from ..leads.enums import LeadSource, LeadStatus
from datetime import datetime
from django.contrib.auth import get_user_model
from apps.accounts.teams.models import Team
from apps.accounts.companies.models import Company

User = get_user_model()

    
class DealViewsTests(TestCase):
    def test_deal_close(self):
        user = User(email='manager@email.com',
                    first_name='sadf', last_name='saldfj', is_superuser=True)
        user.set_password('123')
        user.save()

        company = Company.objects.create(name='Test company')

        team = Team.objects.create(name='Test team', company=company)

        lead = Lead.objects.create(full_name="lead", email="LEAD", assigned_to=user,
                                   source=LeadSource.ADS, status=LeadStatus.QUALIFIED, team=team)
        deal = Deal.objects.create(lead=lead, stage=DealStage.NEGOTIAION, expected_amount=13, probability=13,
                                   expected_close_date=datetime.now())
        client = Client()
        client.login(email='manager@email.com', password='123')
        response = client.post(f'/crm/deals/{deal.id}/update', {'stage': DealStage.LOST,
                                                       "title": "NewDla",
                                                       "expected_amount": 13,
                                                       "probability": 13,
                                                       "expected_close_date": datetime.now().date()})
        
        deal = Deal.objects.get(id=deal.id)
        self.assertEqual(deal.closed_at, datetime.now().date(), msg="Deal closed")