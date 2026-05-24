from django.contrib.auth.forms import AuthenticationForm as DjangoAuthenticationForm
from .models import Membership
from django import forms


class AuthenticationForm(DjangoAuthenticationForm):
    def clean(self):
        data = super().clean()
        user = self.get_user()
        has_membership = Membership.objects.filter(user=user)

        if has_membership:
            if not user.membership.company.is_active:
                raise forms.ValidationError(
                    'Your company account has been deactivated. Please contact your administrator.'
                )
            elif user.membership.team and not user.membership.team.is_active:
                raise forms.ValidationError(
                    'Your team account has been deactivated. Please contact your administrator.'
                )

        return data