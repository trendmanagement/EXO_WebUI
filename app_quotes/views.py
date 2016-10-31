from django.shortcuts import render
from tmqrwebui.models import SiteConfiguration
from app_quotes.contracts_quotes import get_instrument_recent_quotes
from datetime import datetime


# Create your views here.
def view_quotes_monitor(request):
    config = SiteConfiguration.objects.get()

    context = {
        'instruments': config.insruments_list,
        'quotes_info': get_instrument_recent_quotes(config.insruments_list, datetime.now())
    }
    return render(request, 'quotes_monitor.html', context=context)