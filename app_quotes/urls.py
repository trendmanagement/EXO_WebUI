from django.conf.urls import url, include
from django.contrib import admin
from app_quotes.views import *

urlpatterns = [
    url(r"^contracts/$", view_quotes_monitor, name='quotes_contract'),
    url(r"^exo/$", view_quotes_exo, name='quotes_exo'),
]