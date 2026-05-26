from django import forms
from .enums import DealStage
from .models import Deal
from django.db.models import OuterRef, Exists, Q
from ..leads.models import Lead
from ..leads.enums import LeadStatus

closed_stages = [DealStage.WON, DealStage.LOST]


class CreateDealForm(forms.ModelForm):
    probability = forms.IntegerField(
        label='Probability',
        help_text='Enter a number between 0 and 100 (do not include the % symbol)',
        min_value=0,
        max_value=100
    )

    class Meta:
        model = Deal
        exclude = ['closed_at', 'stage', 'actual_amount', 'closed_at']
        help_texts = {'expected_close_date': 'Format: Year-Month-Day'}

    def __init__(self, *args, **kwargs):

        self.user = kwargs.pop('user', None)

        super().__init__(*args, **kwargs)

        self.instance.stage = DealStage.NEGOTIAION
        
        incomplete_deals = Deal.objects.filter(
            lead=OuterRef('pk')
            ).exclude(
                stage__in=[DealStage.WON, DealStage.LOST]
            )

        leads = Lead.objects.annotate(
            has_incomplete=Exists(incomplete_deals)
        ).filter(Q(deals=None) | Q(has_incomplete=False)
                 ).filter(status=LeadStatus.QUALIFIED).distinct()
        self.fields['lead'].queryset = leads

        if self.user.has_perm('crm.local_view_lead'):
            self.fields['lead'].queryset = leads.filter(
            assigned_to=self.user)


class UpdateDealForm(forms.ModelForm):
    class Meta:
        model = Deal
        exclude = ['lead', 'closed_at']
        help_texts = {'expected_close_date': 'Format: Year-Month-Day'}