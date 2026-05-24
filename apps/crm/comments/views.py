from django.views.generic import CreateView, View, DeleteView
from .models import Comment
from ..leads.models import Lead
from ..deals.models import Deal
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseForbidden, JsonResponse
from django.db.models import F
from .forms import CreateCommentForm
from ..mixins import CheckPermissionsMixin


class CreateCommentView(LoginRequiredMixin, CheckPermissionsMixin, CreateView):
    form_class = CreateCommentForm
    keyword = 'add_comment'
       
    def form_invalid(self, form):
        return JsonResponse(form.errors)
    
    def form_valid(self, form):
        comment = form.save(commit=False)
        comment.author = self.request.user
        comment.save()

        return JsonResponse({
            'status': 200
        })
    
    def get_success_url(self):
        ...

    def get_template_name(self):
        ...
    
    
class GetCommentView(LoginRequiredMixin, CheckPermissionsMixin, View):
    keyword = 'view_comment'
    
    def get(self, request, type, id, *args, **kwargs):
        if type and id:
            comments = []

            if type in ['lead', 'l']:
                lead = Lead.objects.filter(assigned_to=request.user).filter(id=id)

                if lead:
                    comments = Comment.objects.prefetch_related('author'
                                                                ).annotate(
                                                                    author_email=F('author__email')
                                                                ).filter(author=request.user, lead=lead.first()
                                                      ).values('id', 'author_email', 'content', 'created_at')
            elif type in ['deal', 'd']:
                deal = Deal.objects.filter(lead__assigned_to=request.user).filter(id=id)

                if deal:
                    comments = Comment.objects.prefetch_related('author'
                                                                ).annotate(
                                                                    author_email=F('author__email')
                                                                ).filter(author=request.user, deal=deal.first()
                                                      ).values('id', 'author_email', 'content', 'created_at')

            return JsonResponse({
                'comments': list(comments)
            })   