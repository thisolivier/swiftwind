from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import CreateView
from django.views.generic import UpdateView
from django.views.generic.list import ListView

from swiftwind.housemates.forms import HousemateUpdateForm
from .forms import HousemateCreateForm
from .models import Housemate


class HousemateListView(LoginRequiredMixin, ListView):
    template_name = 'housemates/list.html'
    context_object_name = 'housemates'
    queryset = Housemate.objects.all()\
        .order_by('user__is_active', 'user__first_name', 'user__last_name')\
        .select_related('user', 'account')


class HousemateCreateView(LoginRequiredMixin, CreateView):
    template_name = 'housemates/create.html'
    form_class = HousemateCreateForm

    def get_success_url(self):
        return reverse('housemates:list')


class HousemateUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'housemates/update.html'
    form_class = HousemateUpdateForm
    model = Housemate
    slug_url_kwarg = 'uuid'
    slug_field = 'uuid'
    context_object_name = 'housemate'

    def get_success_url(self):
        return reverse('housemates:list')


class HousematesRequiredMixin(object):
    """Require that some housemates have been created"""

    def dispatch(self, request, *args, **kwargs):
        if Housemate.objects.exists():
            return super().dispatch(request, *args, **kwargs)
        else:
            return TemplateResponse(
                request=request,
                template='housemates/housemates_required_error.html'
            )
