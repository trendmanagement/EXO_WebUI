from django.conf.urls import url, include
from django.contrib import admin
from tmqr_backend.views import *

urlpatterns = [
    url(r"^contracts/$", view_quotes_monitor, name='quotes_contract'),
    url(r"^exo/$", view_quotes_exo, name='quotes_exo'),
    url(r"^alphas/$", view_actual_alphas, name='quotes_actual_alphas'),
    url(r"^gmifees/(\d{4}-\d{2}-\d{2})/(\d{4}-\d{2}-\d{2})$", view_fcm_fees, name='gmi_fees'),
    url(r"^gmiaccountperformance/(\d{4}-\d{2}-\d{2})/(\d{4}-\d{2}-\d{2})$", view_account_performance, name='gmi_accounts'),

    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]