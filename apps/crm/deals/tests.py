from django.test import TestCase, Client
from .models import Lead, Deal
from .enums import LeadSource, DealStage, LeadStatus
from apps.accounts.models import User
from datetime import datetime

    
class DealViewsTests(TestCase):
    def test_deal_close(self):
        user = User.objects.create_user(username="username", email='manager@email.com',
                                        password='123', first_name='sadf', last_name='saldfj', is_superuser=True)
        lead = Lead.objects.create(full_name="lead", email="LEAD", assigned_to=user,
                                   source=LeadSource.ADS, status=LeadStatus.QUALIFIED)
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