from django.test import TestCase
from .models import User
from django.contrib.auth.models import Group
from ..teams.models import Team
from ..models import Membership
from ..companies.models import Company
from django.test import Client


class UserViewsTests(TestCase):
    def test_user_creation_with_membership(self):
        company = Company.objects.create(name='Test Company')
        user = User.objects.create(
            first_name='test',
            last_name='teamadmin',
            role=Group.objects.get(name='team_admin'),
            email='test_team_admin@email.com'
        )
        user.set_password('123')
        user.save()

        team = Team.objects.create(name='Team 1', company=company)

        Membership.objects.create(user=user, team=team, company=company)

        client = Client()
        login_result = client.login(email='test_team_admin@email.com', password='123')

        response = client.post('/accounts/users/create/', {'first_name': 'test',
                                                           'last_name': 'user',
                                                           'email': 'test_user@email.com',
                                                           'password': 123,
                                                           'team': team.id,
                                                           'role': Group.objects.get(name='manager').id})
        u = User.objects.get(email='test_user@email.com')
        membership = Membership.objects.filter(user=u)
        self.assertTrue(membership)