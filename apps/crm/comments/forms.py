from django import forms
from .models import Comment
from ..deals.enums import DealStage


class CreateCommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content', 'deal', 'lead']

    def clean(self):
        data = super().clean()
        deal = data.get('deal')

        if deal and deal.stage in [DealStage.WON, DealStage.LOST]:
            return

        return data