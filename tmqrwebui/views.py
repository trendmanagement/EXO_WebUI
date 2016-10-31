from django.shortcuts import render
from webui.site_settings import *
from tmqrwebui.models import SiteConfiguration

# Create your views here.
def view_mainpage(request):
    config = SiteConfiguration.get_solo()

    context = {
        'site_name': config.site_name,
        'page_name': 'Dashboard',
    }
    return render(request, 'dashboard.html', context=context)